

##################### OPTIONS #####################
## Assumes that all vehicles are split 50-50 at start
# All variables to change
filename = "moco_jtr.rou.xml"
ACC = 100; # % to have as ACC
#options = 'departSpeed="max"'
 options = 'departSpeed="max" departLane="free"'

output_filename = "moco_jtr_out100ACC.rou.xml"




##################### SCRIPT #####################
MAN = 100 - ACC;
rand = Random.new(Random.new_seed)

f = File.open(filename, "r");
fo = File.open(output_filename, "w");
vehcounter = 1;

f.each_line do |line|
  # Reads only these lines
  # <vehicle id="0.0" depart="0.00" color="green">
  #<vehicle depart="0" id="veh1" route="81" type="CarA" departSpeed="max"/>
  if line =~ /<routes/
    fo.write(line) # Set car definitions at the start
  
    fo.write('    <vType id="CarA" length="5.0" color="0,1,0" accel="1.5" decel="3.0" tau="1.1" sigma="0.0" impatience="0.0" minGap="3.0" maxSpeed="70.0" laneChangeModel="DK2008"/>')
    fo.write("\n")
    fo.write('    <vType id="CarIIDM" length="5.0" color="0,1,0" accel="1.5" decel="3.0" tau="1.1" sigma="0.0" impatience="0.0" minGap="0.5" maxSpeed="70.0" laneChangeModel="DK2008" carFollowModel="IIDM"/>')
    fo.write("\n")
    fo.write('    <vType id="CarM" length="5.0" color="1,0,0" accel="1.5" decel="3.0" tau="2.05" sigma="0.0" impatience="0.0" minGap="4.0" maxSpeed="70.0" laneChangeModel="DK2008"/>')
    fo.write("\n")
  elsif line =~  /id="(.*)"/
    #<vehicle depart="0.0" id="veh1" route="1" type="CarM" departSpeed="max"/>
    check = true # check if vehicle was changed
    vtype = $1
    if (rand.rand < ACC/100.0) # change from Manual to ACC
      line.sub!(/id="(\d+).(\d+)"/, "id=\"veh#{vehcounter}\"")
      vehcounter += 1
      line.sub! '>', " type=\"CarA\" #{options}>"
      fo.write(line)
      check = false
    else # change from ACC to Manual
      line.sub!(/id="(\d+).(\d+)"/, "id=\"veh#{vehcounter}\"")
      vehcounter += 1
      line.sub! '>', " type=\"CarM\" #{options}>"
      fo.write(line)
      check = false
    end
    if check
      fo.write(line)
    end
    
  else
    fo.write(line) # Always write at end if no changes
  end
end

f.close
fo.close
