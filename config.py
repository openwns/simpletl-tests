### constanzeTestsSimpleTL
# Constanze over UDP and SimpleTL
import openwns
import openwns.node


# import other modules to be loaded
import simpleTL.Component
import openwns.distribution
import constanze.distribution.CDFTables
import constanze
import constanze.traffic
import constanze.node
import constanze.evaluation.default

simulator = openwns.Simulator(simulationModel = openwns.node.NodeSimulationModel())
simulator.maxSimTime = 1.0

numberOfClients = 1
numberOfServers = 1
numberOfStations = numberOfClients

speed = 1E9
meanPacketSize = 1500 * 8
loadFactor = 0.1
throughputPerStation = speed * loadFactor / numberOfStations

simulator.modules.simpletl.channel.capacity = speed

simulator.outputStrategy = openwns.simulator.OutputStrategy.DELETE

class ClientNode(openwns.node.Node):
    tl = None
    #applications = None
    load = None
    logger = None
    def __init__(self, id):
        super(ClientNode, self).__init__("client"+str(id))
        self.logger = openwns.logger.Logger("CONST", "client"+str(id), True) # used for ConstanzeComponent
        self.tl = simpleTL.Component.Component(self, "ClientTL", "127.0.0."+str(id+1))
        self.load = constanze.node.ConstanzeComponent(self, "constanze",self.logger)

class ServerNode(openwns.node.Node):
    tl = None
    #applications = None
    load = None
    logger = None
    def __init__(self, id):
        super(ServerNode, self).__init__("server"+str(id))
        self.logger = openwns.logger.Logger("CONST", "server"+str(id), True) # used for ConstanzeComponent
        self.tl = simpleTL.Component.Component(self, "ServerTL", "137.226.4."+str(id+1))
        self.load = constanze.node.ConstanzeComponent(self, "constanze",self.logger)

for i in xrange(numberOfServers):
    node = ServerNode(i)
    logger = node.logger
    udpListenerBinding = constanze.node.UDPListenerBinding(777, logger)
    udpListenerBinding.udpService = node.tl.udpServiceName
    listener = constanze.node.Listener("listener",logger);
    node.load.addListener(udpListenerBinding, listener)
    simulator.simulationModel.nodes.append(node)

serverNode = ServerNode(0)
for i in xrange(numberOfClients):
    node = ClientNode(i+numberOfServers)
    logger = node.logger
    startTime = 0.01
    startindex = 0
    trafficVariants = 4
    phaseDuration = simulator.maxSimTime / trafficVariants
    duration = phaseDuration - startTime
    
    for trafficindexOffset in xrange(trafficVariants):
        trafficindex = (trafficindexOffset + startindex) % trafficVariants
        if ( trafficindex == 0 ):
            traffic = constanze.traffic.CBR(
                startTime, 
                throughputPerStation, 
                meanPacketSize, 
                duration = duration, 
                parentLogger = logger)
        elif ( trafficindex == 1 ):
            traffic = constanze.traffic.Poisson(
                startTime, 
                throughputPerStation, 
                meanPacketSize, 
                duration = duration, 
                parentLogger = logger)
        elif ( trafficindex == 2 ):
            iatDistribution = openwns.distribution.Fixed(meanPacketSize / throughputPerStation)
            packetSizeDistribution = openwns.distribution.Uniform(2 * meanPacketSize, 8)
            traffic = constanze.traffic.ABR(
                iatDistribution, 
                packetSizeDistribution, 
                offset = startTime, 
                duration = duration, 
                parentLogger = logger)
        elif ( trafficindex == 3 ):
            IPmeanPacketSize = 2056.84 # Bits
            iatDistribution = openwns.distribution.NegExp(IPmeanPacketSize / throughputPerStation)
            packetSizeDistribution = constanze.distribution.CDFTables.IPPacketSizeDataTraffic()
            traffic = constanze.traffic.ABR(
                iatDistribution, 
                packetSizeDistribution, 
                offset = startTime, 
                duration=duration, 
                parentLogger = logger)
        else:
            assert "invalid traffic choice"
        
        startTime += phaseDuration            
        udpBinding = constanze.node.UDPBinding(_domainName = node.tl.domainName,
                                               _destinationDomainName = serverNode.tl.domainName,
                                               _destionationPort = 777,
                                               qosClass = openwns.qos.bestEffortQosClass,
                                               parentLogger = logger)
        udpBinding.udpService = node.tl.udpServiceName
        node.load.addTraffic(udpBinding, traffic)
    
    
    simulator.simulationModel.nodes.append(node)

constanze.evaluation.default.installEvaluation(simulator,
                                               maxPacketDelay = 0.0001,
                                               maxPacketSize = 16000,
                                               maxBitThroughput = 2* throughputPerStation,
                                               maxPacketThroughput = 2 * throughputPerStation/meanPacketSize,
                                               delayResolution = 1000,
                                               sizeResolution = 2000,
                                               throughputResolution = 10000)

openwns.setSimulator(simulator)
