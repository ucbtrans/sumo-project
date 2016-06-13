## trajectories.rb

#index of car to follow
cararr = Array (1..10) # for CarA 
#cari = 154 # for CarM
simple_output = true

# which network output to process
networkname = ARGV[0]
if ARGV[0] == nil
  networkname = "huntcol"
end

f = File.open("./network/output_vtype.xml", "r") # VTypeProbe output
lines = f.readlines
f.close

fo = File.open("./network/#{networkname}.poutput_vtype.txt", "w")

cararr.each do |cari|
  index = 0
  time = -1
  timei = -1
  dist = 0
  currx = 0; curry = 0;
  
  while index < lines.length
    #puts index
    if lines[index] =~ /<timestep time="(.*)">/
      if time == -1
        fo.write("%<c=#{cari}, #{$1}>\n")
        fo.write("arr#{cari} = [\n")
      end
      time = $1.to_f
      timei = time.to_i
    end
    
    if lines[index] =~ /<vehicle id="veh(.*)" lane="(.*)" pos="(.*)" x="(.*)" y="(.*)".*/
      if $1.to_i == cari
        # adds distance (approx) travelled this interval
        if currx != 0 or curry != 0
          dist += ((currx - $4.to_i)**2 + (curry - $5.to_i)**2)**(0.5)
        end
        currx = $4.to_i;
        curry = $5.to_i;
        if simple_output
          fo.write("    #{dist}\n")
        else
          fo.write("  <t=#{timei} -- dist=#{dist}>\n")
        end
      end
    end
    index += 1
  end
  fo.write("];\n")
end

fo.close
