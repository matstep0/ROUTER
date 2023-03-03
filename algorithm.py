# vim:ts=4:sts=4:sw=4:expandtab

import logging
import random

import api

class RandomRouter(api.Algorithm):
    """Routing algorithm that forwards packets in random directions"""
    def tick(self, packets):
        for src, packet in packets:
            self.router.store_packet(packet)
        packets = self.router.stored_packets
        random.shuffle(packets)
        links = self.router.links
        random.shuffle(links)
        for link in links:
            if len(packets) > 0:
                self.router.forward_packet(link, packets[-1])
                packets = packets[0:-1]
    #def add_link(*args):
    #    print("dodalemfunkcjie")
class BFS(api.Algorithm):
    """BFS Algorithm"""
    """kojejnosc wysylania pakietow typu FIFO"""
    def __init__(self, router):
        super().__init__(router)
        self.tick_count = 0
        self.sended =set() #zeby nie odbirac pakietow ktore wyslamem chwile temu
    def tick(self, packets):
        for src, packet in packets:
            self.router.store_packet(packet)
            if packet in self.sended:
                self.router.drop_packet(packet)
        packets = self.router.stored_packets
        links = self.router.links
        if len(packets) >0 :
            self.sended.add(packets[0])
            for link in links:
                self.router.forward_packet(link, packets[0])
                self.router.store_packet(packets[0])
            self.router.drop_packet(packets[0]) #wyrzuc pakiet ktory wyslalem wszystkim
        self.tick_count += 1
class DistanceVectorRouter(api.Algorithm):
    """Distance vector type routing algorithm"""
    def __init__(self, router):
        super().__init__(router)
        self.tick_count = 0
        self.distance = dict()

    @property
    def distance_vector(self):
        return [ (dst, hops) for (dst, (hops,_)) in self.distance.items() ]

    def tick(self, packets):
        self.distance[self.router.id] = (0, None)
        link_map = dict()
        for link in self.router.links:
            link_map[link.dst] = link
        for src, packet in packets:
            if isinstance(packet, api.MetaPacket):
                for dst in [ dst for (dst, (hops, lnk)) in self.distance.items() if lnk is not None and lnk == packet.src ]:
                    del self.distance[dst]
                for dst, hops in packet.payload:
                    if dst not in self.distance or hops+1 < self.distance[dst][0]:
                        self.distance[dst] = (hops+1, packet.src)
            else:
                self.router.store_packet(packet)
        if self.tick_count % 10 == 0:
            for link in self.router.links:
                self.router.forward_packet(link, api.MetaPacket(self.router.id, link.dst, self.distance_vector))
        else:
            link_pkt = dict()
            for packet in self.router.stored_packets:
                dst = self.distance.get(packet.dst, (None, None))[1]
                if dst is None:
                    continue
                lnk = link_map[dst]
                if lnk is not None:
                    if lnk.dst not in link_pkt:
                        self.router.forward_packet(lnk, packet)
                        link_pkt[lnk.dst] = 1
        self.tick_count += 1

class LinkStateRouter(api.Algorithm):
    """Link State type routing algorithm"""
    def __init__(self, router):
        super().__init__(router)
        self.tick_count = 0
        self.graph =dict()
        #print("inicjalizacja",self.graph)
        self.graph_version=0
        self.dir_map={self.router.id:None} # w ktorym kierunku posylac pakiet
    @property
    def generate_Meta(self): #tick count jest "id pakietu" czas od ostatniej zmiany
        #print("generuje",(self.graph_version, self.graph ) )
        return (self.graph_version, self.graph)
    def dijkstra(self,id):
        #print("dijkstrastrat")
        #tablice do dijkstry
        self.skad={self.router.id:self.router.id}
        self.odl={self.router.id:0} #
        todo=set() #wierzcholki do obsluzenia

        todo.add(id)
        #print("todo",todo,"odl",self.odl,"graph",self.graph)
        while len(todo)>0:
            for v_min in todo: break
            for ver in todo:
                if self.odl[ver]<self.odl[v_min]:
                    v_min=ver
            id=v_min #krok dijkstry znajdz najmniejszy
            todo.remove(id)
        #    if not id in self.graph:
        #        self.graph[id]=[]
        #trzeba to ominac
            if id in self.graph: # brak wierzcholak w grafie czyli on nie ma krawedzi
                for vertex in self.graph[id]:
                    if not vertex in self.odl or self.odl[vertex]>self.odl[id]+1:
                        self.odl[vertex]=self.odl[id]+1
                        self.skad[vertex]=id #od kogo byla ta najkrotsza droga
                        todo.add(vertex)
        #mam wszystko policzone , teraz odtworzyc wynik
        #print("graph:",self.router.id,self.graph)
        for vertex in self.skad.keys():
            it=vertex
            #print("it",it)
            #print("pokazslownik",self.skad)
            while self.skad[it]!=self.router.id:
                it=self.skad[it]
            self.dir_map[vertex]=it
            #print("dir_map",self.dir_map)
        #print("dijkstra stop")
    def tick(self, packets):
        if self.tick_count==0: #poczatkowa inicjalizacja
            self.graph[self.router.id]=[link.dst for link in self.router.links] #klucze id wierzcholkow , var to listy sasiadow
        #print("jestem",self.router.id,self.graph)
        link_map = dict()
        for link in self.router.links:
            link_map[link.dst] = link
        toupdate=[]
        graph_copy=self.graph
        for src, packet in packets:
            if isinstance(packet, api.MetaPacket):
                version,graph=packet.payload
                #print("MP",version,graph)
                if version >= self.graph_version:
                    toupdate+=[(version,graph)]
            else:
                self.router.store_packet(packet)
        if len(toupdate)>0:
            toupdate=sorted(toupdate,key=lambda x:x[0]) #upade bedzie on najwczesniejszych do najpozniejszch
            for version,graph in toupdate:
                self.graph.update(graph)
            if graph_copy!=self.graph:
                self.graph_version=toupdate[-1][0]
            my_neight=[link.dst for link in self.router.links]
            if set(my_neight)==set(self.graph[self.router.id]):
                pass
            else: #popraw
                self.graph[self.router.id]=my_neight
                self.graph_version=self.tick_count
            self.dijkstra(self.router.id)#obliczam dir_map
        if self.tick_count % 10 == 0:
            for link in self.router.links:
                self.router.forward_packet(link, api.MetaPacket(self.router.id, link.dst, self.generate_Meta))
        else:

            link_pkt = dict()
            for packet in self.router.stored_packets:
                dst=packet.dst
                #print("src",packet.src)
                #print("dst",dst)
                #print("dir_map",self.dir_map)
                #print("link_map",link_map)
                if dst in self.dir_map:
                    dst = self.dir_map[dst] #mamy id rotera do ktorego posalc
                else:
                    dst = None
                if dst is None:
                    continue
                lnk = link_map[dst]
                if lnk is not None:
                    if lnk.dst not in link_pkt:
                        self.router.forward_packet(lnk, packet)
                        link_pkt[lnk.dst] = 1
        self.tick_count += 1
