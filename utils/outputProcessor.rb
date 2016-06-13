## outputProcessor.rb

# which network output to process
networkname = ARGV[0]
if ARGV[0] == nil
  networkname = "huntcol"
end

# which network output to process
sample = ARGV[1].to_i
if ARGV[1] == nil
  sample = 12
end

f = File.open("./network/#{networkname}.output.xml", "r")
fo = File.open("./network/#{networkname}.poutput.txt", "w")
lines = f.readlines

#puts lines.length
index = 0
time = -1
timei = -1
while index < lines.length
  #puts index
  if lines[index] =~ /<timestep time="(.*)">/
    time = $1.to_f
    timei = time.to_i
    if timei % sample == 0
      fo.write("<t=#{$1}>\n")
    end
  end
  
  if timei % sample == 0
    if lines[index] =~ /<edge id="(.*)">/
      fo.write("  <e=#{$1}>\n")
    end
    
    if lines[index] =~ /<lane id="(.*)">/
      lane = $1
      index += 1
      while lines[index] !~ /<\/lane>/
        if lines[index] =~ /<vehicle id="(.*)" pos="(.*)" speed="(.*)"\/>/
          vehicle = $1
          position = $2
          speed = $3
          fo.write("    <v=#{vehicle} #{lane} #{position} #{speed}>\n")
        end
        index += 1
      end
    end
  end
  index += 1
end
f.close
fo.close

