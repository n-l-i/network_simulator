
import random,math,time
import network_simulator.render as render


def finished():
    time.sleep(10)
    exit()
    

class Simulator:
    def __init__(self,dimensions,img_size):
        self.dimensions = dimensions
        self.node_lst = []
        self.available_positions = []
        for row in range(0,self.dimensions[1]-4,1):
            for col in range(0,self.dimensions[0]-4,1):
                self.available_positions.append((col,row))
        self.packet_lst = []
        self.dead_node_lst = []
        self.img_count = 0
        self.renderer = render.Render(self,dimensions,img_size)
    
    def define_nodes(self, max_range, min_range=0, battery_size=4):
        self.node_max_range = max_range
        self.node_min_range = min_range
        self.node_battery_size = battery_size
    
    def spawn_nodes(self,number_of_nodes,min_distance=None,max_distance=None):
        if min_distance == None: min_distance=(self.node_min_range+self.node_max_range)/2
        if max_distance == None: max_distance=self.node_max_range
        for i in range(0,number_of_nodes):
            while True:
                position = random.choice(self.available_positions)
                if Simulator.good_node_spawn_pos(position,self.node_lst,min_distance,max_distance):
                    break
            self.available_positions.remove(position)
            self.node_lst.append(Node(position,self.node_max_range,self.node_min_range,self.node_battery_size))
            print("node: "+str(i)+" at "+str(position))
        self.create_connections()
    
    def create_connections(self):
        self.connection_lst = []
        for sender in self.node_lst:
            for receiver in self.node_lst:
                if Simulator.node_is_in_range(sender,receiver):
                    connection = (sender,receiver)
                    self.connection_lst.append(connection)
                    #receiver.add_connection(connection)
                    sender.add_connection(connection)
        self.sort_connections()
                    
    def sort_connections(self):
        sorted_lst = []
        distance_lst = []
        for connection in self.connection_lst:
            distance_lst.append(distance_between(connection[0],connection[1]))
        for i in range(0,len(self.connection_lst)):
            lst_index = 0
            for j in range(0,i):
                if distance_lst[i]>distance_lst[j]:
                    lst_index += 1
            sorted_lst.insert(lst_index,self.connection_lst[i])
        self.connection_lst = sorted_lst
                
    def node_is_in_range(sender,receiver):
        if receiver == sender:
            return False
        distance = distance_between(sender,receiver)
        return distance <= sender.get_range()[0] and distance >= sender.get_range()[1]
    
    def good_node_spawn_pos(position,node_lst,min_distance,max_distance):
        is_too_far = True
        for node in node_lst:
            if distance_between(node,position) < min_distance:
                return False
            if distance_between(node,position) < max_distance:
                is_too_far = False
        return (not is_too_far) or len(node_lst)==0
    
    def update(self):
        self.update_packets()
        self.update_connections()
        self.update_nodes()
        self.renderer.render()
        
    def update_packets(self):
        for packet in self.packet_lst[:]:
            packet.get_end_node().receive_pkt(packet)
            self.packet_lst.remove(packet)
            
    def update_connections(self):
        if self.connection_lst:
            for node in self.node_lst:
                if node.get_received_pkts():
                    # nodes that received a pkt will send one
                    neighbours = node.get_neighbours()
                    if not neighbours:
                        continue
                    neighbour = random.choice(neighbours)
                    packet = node.send_new_pkt(neighbour)
                    self.packet_lst.append(packet)
                    print("\tsending pkt: "+str(node.get_coords())+"-"+str(neighbour.get_coords()))
            for node in self.node_lst:
                number_of_nodes = len(self.node_lst)+len(self.dead_node_lst)
                random_number = random.choice(range(0,number_of_nodes*2))
                if random_number>0:
                    continue
                # lucky nodes will send a pkt
                neighbours = node.get_neighbours()
                if not neighbours:
                    continue
                neighbour = random.choice(neighbours)
                packet = node.send_new_pkt(neighbour)
                self.packet_lst.append(packet)
                print("\tsending pkt: "+str(node.get_coords())+"-"+str(neighbour.get_coords()))
                
    def update_nodes(self):
        for node in self.node_lst[:]:
            node.energy_consumption(1)
            if node.is_out_of_power():
                self.node_lst.remove(node)
                self.dead_node_lst.append(node)
                for connection in self.connection_lst[:]:
                    if node in connection:
                        self.connection_lst.remove(connection)
                        sender = connection[0]
                        sender.remove_connection(connection)
            

class Node:
    def __init__(self,coords,max_range,min_range,battery_size):
        self.coords = coords
        self.max_range = max_range
        self.min_range = min_range
        self.battery_size = battery_size
        self.energy_level = 100*self.battery_size
        self.connections = []
        self.neighbours = []
        self.received_pkts = []
    
    def get_coords(self): return self.coords
    def get_range(self): return (self.max_range,self.min_range)
    def get_energy_level(self): return int(self.energy_level/self.battery_size)
    def get_connections(self): return self.connections
    def get_neighbours(self): return self.neighbours
    def get_received_pkts(self): return self.received_pkts

    def add_connection(self,connection):
        if connection in self.connections:
            return
        self.connections.append(connection)
        self.add_neighbour(connection[1-connection.index(self)])
    def remove_connection(self,connection):
        if connection not in self.connections:
            return
        self.connections.remove(connection)
        self.remove_neighbour(connection[1-connection.index(self)])
    def add_neighbour(self,neighbour): self.neighbours.append(neighbour)
    def remove_neighbour(self,neighbour): self.neighbours.remove(neighbour)

    def is_out_of_power(self): return self.energy_level <= 0

    def energy_consumption(self,amount):
        self.energy_level -= amount

    def receive_pkt(self,pkt):
        self.energy_consumption(1*pkt.get_pkt_size())
        self.received_pkts.append(pkt)
        
    def send_new_pkt(self,dest_node):
        self.received_pkts = []
        pkt_size = 8
        self.energy_consumption(3*pkt_size)
        return Packet(pkt_size,self,dest_node)
    

class Packet:
    def __init__(self,pkt_size,start_node,end_node):
        self.pkt_size = pkt_size
        self.start_node = start_node
        self.end_node = end_node

    def get_pkt_size(self): return self.pkt_size
    def get_start_node(self): return self.start_node
    def get_end_node(self): return self.end_node
    
    
def distance_between(a,b):
    if isinstance(a,Node):
        (col_a,row_a) = a.get_coords()
    else:
        (col_a,row_a) = a
    if isinstance(b,Node):
        (col_b,row_b) = b.get_coords()
    else:
        (col_b,row_b) = b
    return math.hypot(col_a-col_b,row_a-row_b)
    


    
