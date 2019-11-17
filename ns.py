
import random,math,time
import network_simulator.render as render


def finished():
    time.sleep(10)
    exit()
    

class Simulator:
    def __init__(self,number_of_nodes,dimensions,img_size,node_range):
        self.dimensions = dimensions
        self.node_range = node_range
        self.create_nodes(number_of_nodes)
        self.create_connections()
        self.packet_lst = []
        self.dead_node_lst = []
        self.img_count = 0
        self.renderer = render.Render(self,dimensions,img_size)
        self.renderer.render()
        
    def create_nodes(self,number_of_nodes):
        self.node_lst = []
        available_positions = []
        for row in range(0,self.dimensions[1]-4,1):
            for col in range(0,self.dimensions[0]-4,1):
                available_positions.append((col,row))
        for i in range(0,number_of_nodes):
            while True:
                position = random.choice(available_positions)
                if self.good_node_spawn_pos(position,self.node_lst):
                    break
            available_positions.remove(position)
            self.node_lst.append(Node(position))
            print("node: "+str(i)+" at "+str(position))
    
    def create_connections(self):
        self.connection_lst = []
        for node_a in self.node_lst:
            for node_b in self.node_lst:
                if self.neigbouring_nodes(node_a,node_b) and not ((node_b,node_a) in self.connection_lst or (node_a,node_b) in self.connection_lst):
                    connection = (node_a,node_b)
                    self.connection_lst.append(connection)
                    node_a.add_connection(connection)
                    node_b.add_connection(connection)
        self.sort_connections()
                    
    def sort_connections(self):
        sorted_lst = []
        distance_lst = []
        for connection in self.connection_lst:
            distance_lst.append(distance_between_nodes(connection[0],connection[1]))
        for i in range(0,len(self.connection_lst)):
            lst_index = 0
            for j in range(0,i):
                if distance_lst[i]>distance_lst[j]:
                    lst_index += 1
            sorted_lst.insert(lst_index,self.connection_lst[i])
        self.connection_lst = sorted_lst
                
    def neigbouring_nodes(self,node_a,node_b):
        if node_a == node_b:
            return False
        distance = distance_between_nodes(node_a,node_b)
        return distance <= self.node_range
    
    def good_node_spawn_pos(self,position,node_lst):
        min_distance = self.node_range/2
        max_distance = self.node_range
        is_too_far = True
        for node in node_lst:
            if distance_between_nodes(node,Node(position)) < min_distance:
                return False
            if distance_between_nodes(node,Node(position)) < max_distance:
                is_too_far = False
        return (not is_too_far) or len(node_lst)==0
    
    def update(self):
        self.update_packets()
        self.update_connections()
        self.update_nodes()
        self.renderer.render()
        
    def update_packets(self):
        dead_packets = []
        for packet in self.packet_lst:
            packet.get_end_node().receive_pkt(packet)
            dead_packets.append(packet)
        for packet in dead_packets:
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
                random_number = random.choice(range(0,number_of_nodes*5))
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
        dead_nodes = []
        for node in self.node_lst:
            node.energy_consumption(1)
            if node.is_out_of_power():
                dead_nodes.append(node)
                dead_connections = []
                for connection in node.get_connections():
                    dead_connections.append(connection)
                for connection in dead_connections:
                    self.connection_lst.remove(connection)
                    connection[0].remove_connection(connection)
                    connection[1].remove_connection(connection)
        for node in dead_nodes:
            self.dead_node_lst.append(node)
            self.node_lst.remove(node)
            

class Node:
    def __init__(self,coords):
        self.coords = coords
        self.battery_size = 4
        self.energy_level = 100*self.battery_size
        self.connections = []
        self.neighbours = []
        self.received_pkts = []
    
    def get_coords(self): return self.coords
    def get_energy_level(self): return int(self.energy_level/self.battery_size)
    def get_connections(self): return self.connections
    def get_neighbours(self): return self.neighbours
    def get_received_pkts(self): return self.received_pkts

    def add_connection(self,connection):
        self.connections.append(connection)
        self.add_neighbour(connection[1-connection.index(self)])
    def remove_connection(self,connection):
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
    
    
def distance_between_nodes(node_a,node_b):
    (col_a,row_a) = node_a.get_coords()
    (col_b,row_b) = node_b.get_coords()
    return math.hypot(col_a-col_b,row_a-row_b)
    


    
