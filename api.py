# vim:ts=4:sts=4:sw=4:expandtab

import json
import logging
import random
import uuid

###
#
# Interfaces
#
###
class Packet:
    """Abstract packet class"""
    def __init__(self, src, dst):
        self._id  = str(uuid.uuid4())
        self._src = src
        self._dst = dst
    @property
    def id(self):
        """Returns globally unique id of the packet"""
        return self._id
    @property
    def src(self):
        """Returns address of the source router"""
        return self._src
    @property
    def dst(self):
        """Returns address of the destination router"""
        return self._dst

class MetaPacket(Packet):
    """Packet for routing algorithm communication"""
    def __init__(self, src, dst, payload):
        super().__init__(src, dst)
        self._payload = json.dumps(payload)

    @property
    def payload(self):
        return json.loads(self._payload)
class Link:
    """Abstract inter-router link class"""
    def __init__(self, dst):
        self._dst = dst
    @property
    def dst(self):
        """Returns address of the destination router"""
        return self._dst

class Router:
    """Abstract router class"""
    @property
    def id(self):
        """Returns address of the router"""
        pass
    @property
    def links(self):
        """Returns a list of links available at the router"""
        pass
    @property
    def stored_packets(self):
        """Returns a list of packets stored in the memory of the router"""
        pass
    def drop_packet(self, packet):
        """rops a packet"""
        pass
    def store_packet(self, packet):
        """Stores a packet in the memory of the router"""
        pass
    def forward_packet(self, link, packet):
        """Forwards a packet over a link"""
        pass

class Algorithm:
    """Abstract routing algorithm class"""
    def __init__(self, router):
        if not isinstance(router, Router):
            raise ValueError
        self.router = router
    def __call__(self, packets):
        if not isinstance(packets, list):
            raise ValueError
        for src, packet in packets:
            if not isinstance(packet, Packet):
                raise ValueError
            if src is not None and not isinstance(src, Link):
                raise ValueError
        self.tick(packets)
    def add_link(self, link):
        """Called when new link is added to router"""
        pass
    def del_link(self, link):
        """Called when a link is removed from router"""
        pass
    def tick(self, packets):
        """Called in every round of routing algorithm"""
        pass
