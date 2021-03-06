from abc import abstractmethod
from typing import Dict

from anoncreds.protocol.types import Attribs


class AttrRepo:
    @abstractmethod
    def getAttributes(self, proverId):
        raise NotImplementedError

    @abstractmethod
    def addAttributes(self, proverId, attributes: Attribs):
        raise NotImplementedError


class InMemoryAttrRepo(AttrRepo):
    def __init__(self):
        self.attributes = {}    # type: Dict

    def getAttributes(self, proverId):
        return self.attributes.get(proverId)

    def addAttributes(self, proverId, attributes: Attribs):
        self.attributes[proverId] = attributes
