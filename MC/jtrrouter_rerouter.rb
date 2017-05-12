## inputConverter.rb

# what network is being used
#networkname = ARGV[0]
#if ARGV[0] == nil
  networkname = "moco"
  jtr_output = "moco_jtr"
#end

# duration of simulation
#simduration = ARGV[1].to_i
#if ARGV[1] == nil
  simduration = 60*60
#end

################################################################################################
## Reads in relevant files and organizes data
# Retrieves the list of nodes
nodes = {}
f = File.open("./network/#{networkname}.nod.xml", "r")
f.each_line do |line|
  if line =~ /<node\s*id="([^\s]*)"\s*x="(.*)"\s*y="(.*)"/
    nodes[$1] = [$2, $3]
  end
end
f.close
#puts nodes.to_s

# Retrieves the list of edges
edges = {}
f = File.open("./network/#{networkname}.edg.xml", "r")
f.each_line do |line|
  if line =~ /<edge id="([^\s]*)"\s*from="([^\s]*)"\s*to="([^\s]*)"/
    edges[$1] = [$2, $3]
  end
end
f.close
#puts edges.to_s

# Retrieves the list of edges
connections = Hash.new()
f = File.open("./network/#{networkname}.con.xml", "r")
f.each_line do |line|
  # <connection from="123" to="234" fromLane="0" toLane="0" via=":int_id1" dir="id2" state="id3"/>
  if line =~ /<connection from="([^\s]*)" to="([^\s]*)" fromLane="([^\s]*)" toLane="([^\s]*)" via="([^\s]*)" dir="([^\s]*)" state="([^\s]*)"/
    # $1 is incoming, $2 is outcoming
    if connections[$1] == nil
      connections[$1] = Array.new
    end
    if not connections[$1].include?($2)
      connections[$1].push($2)
    end
  end
end
f.close

# Retrieves the turn information
turns = {}
illegalturns = {}
f = File.open("./network/#{networkname}.turn.xml", "r")
lines = f.readlines 
index = 0
while index < lines.length
  if lines[index] =~ /<fromEdge\s*id="([^\s]*)">/
    src = $1
    turns[src] = {}
    count = 1
    while lines[index+count] =~ /<toEdge\s*id="([^\s]*)"\s*probability="([^\s]*)"\/>/
      newprobability = $2
      newedge = $1
      if newprobability.to_f == 0
        illegalturns[edges[src][1]]= [edges[src][0], edges[newedge][1]]
        count += 1
      else
        turns[src][newedge] = newprobability
        count += 1
      end
    end
    index += count
  end
  index += 1
end
f.close
#puts turns
#puts sources.to_s
#puts sinks.to_s

# Read sources
sources = {}
sinks = []
f = File.open("./network/#{networkname}.flows.xml", "r")
lines = f.readlines 
index = 0
while index < lines.length
  #<flow id='0' from='243728741#0'  begin='0' end='3600' number='999'/>
  if lines[index] =~ /<flow\s*id="([^\s]*)"\s*from="([^\s]*)"\s*begin="([^\s]*)"\s*end="([^\s]*)"\s*number="([^\s]*)"\/>/
    sources[$2] = $5
    #puts $2
    #sinks.push($2) # doesn't work for split lanes
  end
  #if lines[index] =~ /<sink\s*nodes="([^\s]*)"\/>/
  #  sinks.push($1)
  #end
  index += 1
end
f.close
#puts "#{sources}"

# Read parameters
f = File.open("./parameters.txt", "r")
lines = f.readlines
index = 0
autonomous = [0, false]
parametersAuto = [-1, -1, -1, -1, -1, -1, -1, -1]
parametersManu = [-1, -1, -1, -1, -1, -1, -1, -1]
while index < lines.length
  if lines[index] =~ /Percent: (.*)/
    autonomous[0] = $1.to_f
  elsif lines[index] =~ /PlatoonsActive: (.*)/
    if $1 == "Platoons"
      autonomous[1] = true
    end
  elsif lines[index] =~ /AccelerationA: (.*)/
    parametersAuto[0] = $1.to_f
  elsif lines[index] =~ /DecelerationA: (.*)/
    parametersAuto[1] = $1.to_f
  elsif lines[index] =~ /ReactTimeA: (.*)/
    parametersAuto[2] = $1.to_f
  elsif lines[index] =~ /SteppingRateA: (.*)/
    parametersAuto[3] = $1.to_f
  elsif lines[index] =~ /ImperfectionA: (.*)/
    parametersAuto[4] = $1.to_f
  elsif lines[index] =~ /ImpatienceA: (.*)/
    parametersAuto[5] = $1.to_f
  elsif lines[index] =~ /MinGapA: (.*)/
    parametersAuto[6] = $1.to_f
  elsif lines[index] =~ /MaxSpeedA: (.*)/
    parametersAuto[7] = $1.to_f
  elsif lines[index] =~ /AccelerationM: (.*)/
    parametersManu[0] = $1.to_f
  elsif lines[index] =~ /DecelerationM: (.*)/
    parametersManu[1] = $1.to_f
  elsif lines[index] =~ /ReactTimeM: (.*)/
    parametersManu[2] = $1.to_f
  elsif lines[index] =~ /SteppingRateM: (.*)/
    parametersManu[3] = $1.to_f
  elsif lines[index] =~ /ImperfectionM: (.*)/
    parametersManu[4] = $1.to_f
  elsif lines[index] =~ /ImpatienceM: (.*)/
    parametersManu[5] = $1.to_f
  elsif lines[index] =~ /MinGapM: (.*)/
    parametersManu[6] = $1.to_f
  elsif lines[index] =~ /MaxSpeedM: (.*)/
    parametersManu[7] = $1.to_f
  end
  index += 1
end
f.close
#puts autonomous
#puts parametersAuto
#puts parametersManu

################################################################################################
## Finds and organizes possible routes with probabilities
def findPath(source, sink, edges, path, illegalturns)
  # If we completed the path, return
  if source == sink
    return path
  end
  
  # Go through each edge out of here  
  puts edges
  edges.keys.each { |edge|
    if edges[edge][0] == source # we found an edge out
      if (not illegalturns[source]) || (not path.include?(illegalturns[source][0])) or illegalturns[source][1] != edges[edge][1]
        # does not match to an illegal turn
        nxt = edges[edge][1]
        # check to make sure we haven't been here already
        if not path.include?(nxt)
          temp = findPath(nxt, sink, edges, path.clone.push(nxt), illegalturns)
          if temp
            return temp
          end
        end
      else
        # This turn is not legal
      end
    end
  }
  # If we went through all edges and found no new unique path return empty
  return nil
end

def getEdge(node1, node2, edges)
  edges.keys.each { |edge|
    if edges[edge][0] == node1 and edges[edge][1] == node2
      return edge
    end
  }
end

def toEdges(array, edges)
  array2 = []
  i = 0
  while i < array.length - 1
    array2.push getEdge(array[i], array[i+1], edges)
    i += 1;
  end
  return array2
end

def cleanPrint(array)
  str = ""
  array.each{ |elem|
    str += (elem.to_s + " ");
  }
  return (str.strip!)
end

def getProbability(route, turns, connections)
  probability = 1
  prob = 1
  i = 0
  #print "Turning from #{cleanPrint(route)} "
  while i < route.length - 1
    curr_edge = route[i]
    if turns[curr_edge] == nil
      #puts connections[curr_edge]
      if connections[curr_edge] != nil
        prob = 1.0 / connections[curr_edge].length
      else
        prob = 1.0
      end
    else
      prob = turns[route[i]][route[i+1]]
      if prob == nil
        prob = 0
      end
    end
    #print "#{prob} "
    probability *= prob.to_f
    i += 1;
  end
  #puts "has probability #{probability}"
  return probability
end

################################################################################################
# Writes the route file
f = File.open("./network/#{networkname}.rou.xml", "w")
f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<routes>\n");
f.write("  <vType id=\"CarA\" length=\"5.0\" color=\"0,1,0\" accel=\"#{parametersAuto[0]}\" decel=\"#{parametersAuto[1]}\" tau=\"#{parametersAuto[2]}\" stepping=\"#{parametersAuto[3]}\" sigma=\"#{parametersAuto[4]}\" impatience=\"#{parametersAuto[5]}\" minGap=\"#{parametersAuto[6]}\" maxSpeed=\"#{parametersAuto[7]}\"/>\n");
f.write("  <vType id=\"CarM\" length=\"5.0\" color=\"1,0,0\" accel=\"#{parametersManu[0]}\" decel=\"#{parametersManu[1]}\" tau=\"#{parametersManu[2]}\" stepping=\"#{parametersManu[3]}\" sigma=\"#{parametersManu[4]}\" impatience=\"#{parametersManu[5]}\" minGap=\"#{parametersManu[6]}\" maxSpeed=\"#{parametersManu[7]}\"/>\n");
f.write("\n");

## At each source, create the possible routes to sinks
# Go through each source
route_id = 0;
routes = Hash.new() # can't initialize default here or causes a bug
all_routes = []

f_jtr = File.open("./network/#{jtr_output}.rou.xml", "r")
lines = f_jtr.readlines 
index = 0
while index < lines.length
  # <route edges="50846710#1.45 -143009954 143009954 -142530979 244626213#3 50846744 50846724#0 50846724#1"/>
  if lines[index] =~ /<route edges="(.*)"\/>/
    edges_str = $1
    edges_arr = edges_str.gsub(/\s+/, ' ').strip.split(" ")
    if (edges_arr.uniq.length == edges_arr.length) and (not (all_routes.include? edges_arr))
      # This is a valid route
      route = edges_arr
      all_routes.push(route)
      source = route[0]
      
      #puts cleanPrint(route)
      #puts route.length 
      #puts "----"
      # if the route is non-trivial, let's add it as a route
      if route.length > 1
        #puts route_id
        #puts getProbability(route, turns)
        #puts cleanPrint(route)
        #puts "----"
        #puts cleanPrint(routes[source])
        #puts "----"
        route_id += 1
        #puts "Source: #{source} and route: #{route.to_s}"
        if routes[source] == nil
          routes[source] = Array.new
        end
        routes[source]  = routes[source].push([route, getProbability(route, turns, connections), route_id])
        #puts "#{routes[source]}"
        #puts "#{routes}"
        #puts "---"
        #puts routes[source].to_s
        f.write("  <route id=\"#{route_id}\" edges=\"#{cleanPrint(route)}\"/>\n");
      end
    end
  end
  index += 1
end
f.write("\n");
f_jtr.close

=begin
sources.keys.each { |source|
  # For each sink, find a path to it
  sinks.each { |sink|
    #puts "Source: #{source} #{sink}"
    #puts "#{source} #{sink} #{illegalturns}"
    puts "End-Start: #{source} #{sink}"
    tpath = findPath(source, sink, edges, [source], illegalturns)
    puts "tpath: #{tpath}"
    if tpath
      route = toEdges(tpath, edges)
  
      # if the route is non-trivial, let's add it as a route
      if route.length > 1
        route_id += 1
        #puts "Source: #{source} and route: #{route.to_s}"
        if routes[source] == nil
          routes[source] = []
        end
      routes[source].insert(0, [route, getProbability(route, turns), route_id])
      #puts routes[source].to_s
      f.write("  <route id=\"#{route_id}\" edges=\"#{cleanPrint(route)}\"/>\n");
      end 
    end
  }
}
f.write("\n");
=end

## Create a set of cars at each source node, and sets a route given probabilities
#puts routes["3"].to_s
rand = Random.new(Random.new_seed)
vehicle_id = 0;

## Rule method, can be changed to poisson, periodic, etc
# given some rate, decides whether a car will be generated (assumes 1 second simulation steps)
def rule (rate, rand)
  r = rand.rand
  return r < rate / (60*60) #60*60 = 3600 seconds
end

## Rate method, can be changed to sinusoidal, etc
# given some rate, decides at what rate a car will be created over timei (assumes 1 second simulation steps)
def rate (raw, time)
  return raw #  raw * cos(time)^2
end

#puts "#{routes.keys}"
#routes.keys.each { |source|
#  puts "#{source}"
#  puts "Route: #{routes[source]}"
#}

# Generate the cars according to rule defined above 
(0..simduration).step(1) do |start_time|
  sources.keys.each { |source|
    if routes[source] != nil # only for sources with valid routes
      i = 0
      totprob = 0;
      #puts "Source: #{source}"
      #puts "Routes at source: #{routes[source]}"
      #puts "Source: #{source}"
      while i < routes[source].length
        totprob += routes[source][i][1]
        i += 1
      end
      #puts totprob
  
      r = rand.rand
      i = 0
      cummulator = 0;
      while i < routes[source].length
        cummulator += routes[source][i][1] / totprob
        if cummulator >= r
          break
        end
        i += 1
      end
  
      # Decides whether to create a car in the given second and generates it
      if routes[source][i] and rule(rate(sources[source].to_f, start_time), rand)
        #puts cummulator
        vehicle_id += 1
        #puts vehicle_id
        #puts "#{start_time} #{vehicle_id} and #{routes[source][i]}"
  
        # whether autonomous or not
        if rand.rand < autonomous[0]/100 # if autonomous
          f.write("  <vehicle depart=\"#{start_time}\" id=\"veh#{vehicle_id}\" route=\"#{routes[source][i][2]}\" type=\"CarA\" departLane=\"free\" departSpeed=\"max\"/>\n");  
        else # if manual vehicle
          #if (routes[source][i][2] == 228) || (routes[source][i][2] == 320) || (routes[source][i][2] == 807)
          #  puts "Source: #{source}"
          #end
          f.write("  <vehicle depart=\"#{start_time}\" id=\"veh#{vehicle_id}\" route=\"#{routes[source][i][2]}\" type=\"CarM\" departLane=\"free\" departSpeed=\"max\"/>\n");
        end
      end
    end
  }
end

f.write("</routes>");
f.close



