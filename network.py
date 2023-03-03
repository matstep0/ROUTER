# vim:ts=4:sts=4:sw=4:expandtab

import api
import random
from random import randint
from math import sqrt
class Network:
    def __init__(self, simulator, algorithm,sed):
        self.simulator = simulator
        random.seed(sed)
    def tick(self, tick_count):
        self.simulator.tick()


class SimpleNetwork(Network):
    def __init__(self, simulator, algorithm,sed):
        super().__init__(simulator, algorithm,sed)

        self.r1 = self.simulator.add_router(algorithm, 'a')
        self.r2 = self.simulator.add_router(algorithm, 'b')
        self.r3 = self.simulator.add_router(algorithm, 'c')
        self.r4 = self.simulator.add_router(algorithm, 'd')
        self.r5 = self.simulator.add_router(algorithm, 'e')
        self.r6 = self.simulator.add_router(algorithm, 'f')
        self.r7 = self.simulator.add_router(algorithm, 'g')
        self.r8 = self.simulator.add_router(algorithm, 'h')
        self.simulator.add_link(self.r1, self.r2)
        self.simulator.add_link(self.r2, self.r3)
        self.simulator.add_link(self.r3, self.r4)
        self.simulator.add_link(self.r4, self.r5)
        self.simulator.add_link(self.r5, self.r6)
        self.simulator.add_link(self.r6, self.r7)
        self.simulator.add_link(self.r7, self.r8)
        self.simulator.add_link(self.r8, self.r1)

    def tick(self, tick_count):
        if tick_count % 2 == 0:
            self.simulator.add_packet(self.r1, self.r4)
        super().tick(tick_count)
class hypercube(Network):
    def __init__(self, simulator, algorithm,sed):
        random.seed(sed)
        super().__init__(simulator, algorithm,sed)
        self.n=5 #wymiar hiperkoski
        self.routery=[None]*(2**self.n) #lista wierzcholkow
        for x in range(2**self.n):
            self.routery[x]=self.simulator.add_router(algorithm,str(x))
        for a in range(2**self.n):
            for b in range(2**self.n):
                if(bin(a^b).count("1")==1):#distance 1
                    self.simulator.add_link(self.routery[a],self.routery[b])
    def tick(self, tick_count):
        a,b=self.routery[randint(0,2**self.n-1)],self.routery[randint(0,2**self.n-1)]
        if a!=b: self.simulator.add_packet(a,b)
        super().tick(tick_count)
class awaria(Network):
    def __init__(self, simulator, algorithm,sed):
        super().__init__(simulator, algorithm,sed)
        self.n=32#dlugosc cyklu
        self.routery=[None]*self.n
        for i in range(self.n):
            self.routery[i]=self.simulator.add_router(algorithm)
        for i in range(self.n):
            self.simulator.add_link(self.routery[i],self.routery[(i+1)%self.n])
        #uszkadzana bedzie ta n-1 <-> 0
    def tick(self, tick_count):
        a,b=self.routery[randint(0,self.n-1)],self.routery[randint(0,self.n-1)]
        if a!=b : self.simulator.add_packet(a,b)
        if tick_count % 5 == 0:#na przemian usuwa i dodaje krawedz
            if (self.routery[self.n-1],self.routery[0]) in self.simulator.links \
or (self.routery[0],self.routery[self.n-1]) in self.simulator.links:
                self.simulator.del_link(self.routery[self.n-1],self.routery[0])
            else:
                self.simulator.add_link(self.routery[self.n-1],self.routery[0])
        super().tick(tick_count)
class randomgeographic(Network):
    """moving router in random_geographic_graph"""

    def connected(self,v1,v2): #check if 2 vertex are connected
        dist=sqrt((v1.position[0]+v2.position[0])**2+(v1.position[1]+v2.position[1])**2)
        return dist<=self.max_signal_distance

    class vertex():
        def __init__(self,simulator,algorithm,size):
            self.simulator=simulator
            self._id=self.simulator.add_router(algorithm)
            self._size=size
            self._position=(randint(0,self._size),randint(0,self._size))
            vx,vy=(randint(0,self._size),randint(0,self._size))
            self._speed=(vx/sqrt(vx**2+vy**2+1),vy/sqrt(vx**2+vy**2)+1) #predkosc znormalizowana do 1
        @property
        def position(self):
            return self._position
        @property
        def speed(self):
            return self._speed
        @property
        def id(self):
            return self._id
        def tick(self):
            self._position[0]==(self._position[0]+self._speed[0])%self._size #moze z drugiej sie pojawic
            self._position[1]==(self._position[1]+self._speed[1])%self._size
            return

    def update_links(self):
        for i in range(self.n): #dodajemy poczatkowe linki
            for j in range(self.n):
                if i!=j and self.connected(self.vert[i],self.vert[j]):
                    self.simulator.add_link(self.vert[i].id,self.vert[j].id)
                if i!=j and not self.connected(self.vert[i],self.vert[j]):
                    self.simulator.del_link(self.vert[i].id,self.vert[j].id)
    def __init__(self, simulator, algorithm,sed):
        random.seed(sed)
        super().__init__(simulator, algorithm,sed)
        self.n=100 #liczba routerow
        self.size=100 #rozmiary kwadratu size x size bedacego plansza
        self.max_signal_distance=sqrt(2)*self.size/2 # zasieg sygnalu
        self.vert=[None]*self.n
        for i in range(self.n): #tworz routery
            self.vert[i]=self.vertex(self.simulator,algorithm,self.size)
    def tick(self,tick_count):
        for v in self.vert:
            v.tick()
        self.update_links()
        a,b=self.vert[randint(0,self.n-1)].id,self.vert[randint(0,self.n-1)].id
        if a!=b: self.simulator.add_packet(a,b)
        super().tick(tick_count)
