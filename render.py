import os,sys,random,subprocess
sys.path.append(os.getcwd()+"/pythonGraphics")
import network_simulator.pythonGraphics.graphics as graphics



class Render:
    def __init__(self,simulator,dimensions,img_size):
        self.simulator = simulator
        self.dimensions = dimensions
        self.tile_size = (int(img_size[0]/dimensions[0]),int(img_size[1]/dimensions[1]))
        self.graphics_window = graphics.GraphWin("Network Simulator",img_size[0],img_size[1],autoflush=False)
        self.img = graphics.Image(graphics.Point(0,0),img_size[0],img_size[1])
        self.img_count = 0


    def render(self):
        # render background
        upper_left_corner = (0,0)
        lower_right_corner = (self.dimensions[0]*self.tile_size[0],self.dimensions[1]*self.tile_size[1])
        draw_rectangle(upper_left_corner,lower_right_corner,"white",self.graphics_window)
        # render connections
        for connection in self.simulator.connection_lst:
            string_value = int(''.join(str(ord(c)) for c in str(connection)))
            string_value = string_value % 0xFFFF
            random_color = "#"+str(hex(string_value))[2:].zfill(6)
            self.render_connection(connection,random_color)
        # render nodes
        for node in self.simulator.node_lst:
            self.render_node(node,"red")
        for node in self.simulator.dead_node_lst:
            self.render_node(node,"grey")
        # render packets
        for packet in self.simulator.packet_lst:
            connection = (packet.get_start_node(),packet.get_end_node())
            self.render_connection(connection,"magenta")
            #self.render_node(packet.get_start_node(),"blue1")
            #self.render_node(packet.get_end_node(),"red4")
        graphics.update(30)
        #save_as_png(self.graphics_window,"~/Desktop/ns4/Images_py/her_"+str(self.img_count))
        #print("img: "+str(self.img_count))
        self.img_count += 1

    def render_node(self,node,color_a):
        color_b = "white"
        color_c = "black"
        color_text = "black"
        (col,row) = node.get_coords()
        centre_point = ((col+2)*self.tile_size[0],(row+2)*self.tile_size[1])
        radius = (int(1.5*self.tile_size[0]),int(1.5*self.tile_size[1]))
        draw_rectangle(centre_point,radius,color_a,self.graphics_window)
        radius = (int(0.5*self.tile_size[0]),int(0.5*self.tile_size[1]))
        draw_rectangle(centre_point,radius,color_b,self.graphics_window)
        radius = (int(0.2*self.tile_size[0]),int(0.2*self.tile_size[1]))
        draw_rectangle(centre_point,radius,color_c,self.graphics_window)
        text_centre_point = ((col+2)*self.tile_size[0],(row+3)*self.tile_size[1])
        text_size = 8
        text = str(node.get_energy_level())+"\n"+str(node.get_coords())
        draw_text(text,text_centre_point,text_size,color_text,self.graphics_window)
        
        
    def render_connection(self,connection,color):
            (node_a,node_b) = connection
            (col_a,row_a) = node_a.get_coords()
            (col_b,row_b) = node_b.get_coords()
            if abs(col_a-col_b)<abs(row_a-row_b):
                c_diff = 0.7
                r_diff = 0
            else:
                c_diff = 0
                r_diff = 0.7
            point_a = ((col_a+2+c_diff)*self.tile_size[0],(row_a+2+r_diff)*self.tile_size[1])
            point_b = ((col_b+2-c_diff)*self.tile_size[0],(row_b+2-r_diff)*self.tile_size[1])
            point_partway = []
            for i in range(4,40):
                i_4 = i/4
                point_partway.append((((i_4-1)*point_a[0]+point_b[0])/i_4,((i_4-1)*point_a[1]+point_b[1])/i_4))
            width = 2
            #draw_line(point_a,point_b,width,color,self.graphics_window)
            for i in range(0,len(point_partway)):
                draw_line(point_a,point_partway[i],width+i/3,color,self.graphics_window)
                


def draw_rectangle(centre_point,radius,color,graphics_window):
    (col,row) = centre_point
    (radius_c,radius_r) = radius
    a = graphics.Rectangle(graphics.Point(col-radius_c,row-radius_r),graphics.Point(col+radius_c,row+radius_r))
    a.setFill(color)
    a.setWidth(0)
    a.draw(graphics_window)
    
def draw_line(point_a,point_b,width,color,graphics_window):
    (col_a,row_a) = point_a
    (col_b,row_b) = point_b
    a = graphics.Line(graphics.Point(col_a,row_a),graphics.Point(col_b,row_b))
    a.setFill(color)
    a.setWidth(width)
    a.draw(graphics_window)
    
    
def draw_text(text,centre_point,text_size,color,graphics_window):
    (col,row) = centre_point
    
    for i in range(-2,3):
        e = []
        e.append(graphics.Text(graphics.Point(col+i,row),text))
        e.append(graphics.Text(graphics.Point(col,row+i),text))
        e.append(graphics.Text(graphics.Point(col+i,row+i),text))
        e.append(graphics.Text(graphics.Point(col+i,row-i),text))
        for ei in e:
            ei.setSize(text_size)
            ei.setStyle("bold")
            ei.setTextColor("white")
            ei.draw(graphics_window)
    
    a = graphics.Text(graphics.Point(col,row),text)
    a.setSize(text_size)
    a.setStyle("bold")
    a.draw(graphics_window)
    

def save_as_png(graphics_window,fileName):
    # save postscipt image 
    graphics_window.postscript(file = fileName+'.eps')
    # convert to png
    command = "convert -density 300 "+fileName+".eps "+fileName+".png; rm "+fileName+".eps "
    subprocess.Popen(command,shell=True)
