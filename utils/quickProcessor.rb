

time = 0;
veh = Hash.new([]);
vehx = Hash.new([]);
vehy = Hash.new([]);
vehsp = Hash.new([]);
vehtime = Hash.new([]);
f = File.open("./output_vtype.xml", "r")
f.each_line do |line|
  if line =~ /    <timestep time="(.*)" id="veh5" vType=""\>/
    time = $1
  end 
  if line =~ /\<vehicle id="(.*)" lane="(.*)" pos="(.*)" x="(.*)" y="(.*)" speed="(.*)"\/\>/
    if $1 == "veh28" #4, 10, 16, 22, 28
      puts $6
    end
    vehx[$1].push($4)
    vehy[$1].push($5)
    vehsp[$1].push($6)
    vehtime[$1].push(time)
  end 
end
puts vehtime
f.close


f = File.open("./stuffs.rou.xml", "w")
x = vehx["veh1"]
y = vehy["veh1"]

#vehtime["veh1"].each
f.write("");


f.close