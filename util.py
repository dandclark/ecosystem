#
#    Dan Clark
#    thedanclark@gmail.com
#    15 June 2013
#
#    util.py
#    Ecosystem
#

import math

LOGGING = False

class Location:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"
        
    # Returns the Euclidean distance between this and otherLocation
    def distanceFrom(self, otherLocation):
        return math.sqrt((self.x - otherLocation.x)**2 + (self.y - otherLocation.y)**2)
    
    
# From the array of organisms, returns an array of organisms within the given radius
# from the given location.
def getOrganismsInRadius(organisms, location, radius):
    organismsInRadius = []
    for organism in organisms:
        if organism.location.distanceFrom(location) <= radius:
            organismsInRadius.append(organism)
    return organismsInRadius
    
# From the array of organisms, returns an array of living organisms within the given radius
# from the given location who have the given type.
def getLivingOrganismsInRadiusWithType(organisms, location, radius, type):
    organismsInRadius = []
    for organism in organisms:
        if isinstance(organism, type) and organism.isAlive and \
                organism.location.distanceFrom(location) <= radius:
            organismsInRadius.append(organism)
    return organismsInRadius
    