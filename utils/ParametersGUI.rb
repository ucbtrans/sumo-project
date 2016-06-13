
# This Shoes-based GUI helps create the file which sets paremeters

require 'yaml/store'

useGUI = true

if useGUI
Shoes.app :title => "Simulation Parameters", :width => 800, :height => 400, :resizable => false do
  background white..white
  
  stack do # options
    flow do
      para ""
    end
    flow do
      para "Percent autonomous:"
      @percent = edit_line "50", margin=> [0, 5, 0, 5]
      para "               "
      list_box items: ["Platoons", "None"],
      width=> 120, choose: "Platoons" do |platoons|
        @platoons.text = platoons.text
      end
      @platoons = para;
    end
    flow do
      para "                              "
      para "Autonomous Class Properties"
      para "            "
      para "Manual Class Properties"
    end
    flow do
      para "Acceleration", margin: [0, 5, 0, 5]
      para "              "
      list_box items: ["2.2", "2.4", "2.6", "2.8", "3.0"],
      width: 120, choose: "2.6" do |accel1|
        @accel1.text = accel1.text
      end
      @accel1 = para;
      para "                             "
      list_box items: ["2.2", "2.4", "2.6", "2.8", "3.0"],
      width: 120, choose: "2.6" do |accel2|
        @accel2.text = accel2.text
      end
      @accel2 = para;
    end
    flow do
      para "Deceleration", margin: [0, 5, 0, 5]
      para "             "
      list_box items: ["4.1", "4.3", "4.5", "4.7", "4.9"],
      width: 120, choose: "4.5" do |decel1|
        @decel1.text = decel1.text
      end
      @decel1 = para;
      para "                             "
      list_box items: ["4.1", "4.3", "4.5", "4.7", "4.9"],
      width: 120, choose: "4.5" do |decel2|
        @decel2.text = decel2.text
      end
      @decel2 = para;
    end
    flow do
      para "Reaction time", margin: [0, 5, 0, 5]
      para "            "
      list_box items: ["1.0", "1.1", "1.2", "1.4", "1.8"],
      width: 120, choose: "1.0" do |react1|
        @react1.text = react1.text
      end
      @react1 = para;
      para "                            "
      list_box items: ["1.0", "1.1", "1.2", "1.4", "1.8"],
      width: 120, choose: "1.0" do |react2|
        @react2.text = react2.text
      end
      @react2 = para;
    end
    flow do
      para "Stepping rate", margin: [0, 5, 0, 5]
      para "            "
      list_box items: ["0.1", "0.25", "0.6", "1.0", "1.5"],
      width: 120, choose: "0.1" do |stepping1|
        @stepping1.text = stepping1.text
      end
      @stepping1 = para;
      para "                             "
      list_box items: ["0.1", "0.25", "0.6", "1.0", "1.5"],
      width: 120, choose: "1.0" do |stepping2|
        @stepping2.text = stepping2.text
      end
      @stepping2 = para;
    end
    flow do
      para "Driver imperfection", margin: [0, 5, 0, 5]
      para "   "
      list_box items: ["0.0", "0.25", "0.5", "0.75", "1.0"],
      width: 120, choose: "0.0" do |imperf1|
        @imperf1.text = imperf1.text
      end
      @imperf1 = para;
      para "                             "
      list_box items: ["0.0", "0.1", "0.25", "0.5", "0.75", "1.0"],
      width: 120, choose: "0.1" do |imperf2|
        @imperf2.text = imperf2.text
      end
      @imperf2 = para;
    end
    flow do
      para "Driver impatience", margin: [0, 5, 0, 5]
      para "     "
      list_box items: ["0.0", "0.1", "0.4", "0.7", "1.0"],
      width: 120, choose: "0.0" do |impat1|
        @impat1.text = impat1.text
      end
      @impat1 = para;
      para "                             "
      list_box items: ["0.0", "0.1", "0.4", "0.7", "1.0"],
      width: 120, choose: "0.1" do |impat2|
        @impat2.text = impat2.text
      end
      @impat2 = para;
    end
    flow do
      para "Minimum gap", margin: [0, 5, 0, 5]
      para "            "
      list_box items: ["1.0", "1.5", "2.0", "2.5", "4.0"],
      width: 120, choose: "1.5" do |minGap1|
        @minGap1.text = minGap1.text
      end
      @minGap1 = para;
      para "                             "
      list_box items: ["1.0", "1.5", "2.0", "2.5", "4.0"],
      width: 120, choose: "2.0" do |minGap2|
        @minGap2.text = minGap2.text
      end
      @minGap2 = para;
    end
    flow do
      para "Maximum speed", margin: [0, 5, 0, 5]
      para "       "
      list_box items: ["40", "55", "70", "85", "100"],
      width: 120, choose: "70" do |maxSpeed1|
        @maxSpeed1.text = maxSpeed1.text
      end
      @maxSpeed1 = para;
      para "                             "
      list_box items: ["40", "55", "70", "85", "100"],
      width: 120, choose: "70" do |maxSpeed2|
        @maxSpeed2.text = maxSpeed2.text
      end
      @maxSpeed2 = para;
    end

    flow do
      para "                                                            "
      button "Create file" do
        File.open('./parameters.txt', 'w') do |addTo|
          addTo.puts("Percent: #{@percent.text}") 
          addTo.puts("PlatoonsActive: #{@platoons.text}") 
          addTo.puts("") 
          addTo.puts("Autonomous settings::") 
          addTo.puts("AccelerationA: #{@accel1.text}") 
          addTo.puts("DecelerationA: #{@decel1.text}") 
          addTo.puts("ReactTimeA: #{@react1.text}") 
          addTo.puts("SteppingRateA: #{@stepping1.text}") 
          addTo.puts("ImperfectionA: #{@imperf1.text}") 
          addTo.puts("ImpatienceA: #{@impat1.text}") 
          addTo.puts("MinGapA: #{@minGap1.text}") 
          addTo.puts("MaxSpeedA: #{@maxSpeed1.text}") 
          addTo.puts("") 
          addTo.puts("Manual settings::") 
          addTo.puts("AccelerationM: #{@accel2.text}") 
          addTo.puts("DecelerationM: #{@decel2.text}") 
          addTo.puts("ReactTimeM: #{@react2.text}") 
          addTo.puts("SteppingRateM: #{@stepping2.text}") 
          addTo.puts("ImperfectionM: #{@imperf2.text}") 
          addTo.puts("ImpatienceM: #{@impat2.text}") 
          addTo.puts("MinGapM: #{@minGap2.text}") 
          addTo.puts("MaxSpeedM: #{@maxSpeed2.text}") 
        end
      end
    end
    
  end # end of options
end
end
  
puts "hey"