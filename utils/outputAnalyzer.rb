
networkname = ARGV[0]
if ARGV[0] == nil
  networkname = "huntcol"
end

interval = ARGV[1]
if ARGV[1] == nil
  interval = 2
end

## A simple file that can analyze how busy certain roads are over time
f = File.open("./network/#{networkname}.poutput.txt", "r")
fo = File.open("./network/#{networkname}.doutput.txt", "w") # volume information for each TIME FRAME separately
lines = f.readlines
edges = {}
tindex = 0
#puts lines.length
index = 0
while index < lines.length
  #puts index
  #puts lines[index]
  if lines[index] =~ /<t=(.*)>/
    time = $1.to_f
    
    # if at a time we want to sample
    if time.to_i % interval == 0
      fo.write("t=#{time}\n")
      index += 1
      # go through each edge
      while lines[index] =~ /<e=(.*)>/
        edge = $1
        population = 0
        index += 1
        
        # add population for each car
        while lines[index] =~ /<v=(.*) (.*) (.*) (.*)>/
          population += 1
          index += 1
        end
        if edges[edge] == nil
          edges[edge] = []
        end
        edges[edge][tindex] = population
        #puts edges[edge]
        fo.write("  #{edge} #{population}\n")
      end
      tindex += 1
    end
  end
  index += 1
end
f.close
fo.close

puts edges.keys
fo2 = File.open("./network/#{networkname}.doutput2.txt", "w") # volume information for each ROAD separately
edges.keys.each{ |edge|
  i = 0
  line = "#{edge} "
  while i < edges[edge].length
    line += "#{edges[edge][i] || 0} "
    i += 1
  end
  line += "\n"
  fo2.write(line)
  puts line
}
fo2.close
