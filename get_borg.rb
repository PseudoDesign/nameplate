# This script loads the borg sources for this project, then moves this
# directory into the borg folder.
require "FileUtils"

PROJECT_NAME = "borg"
parent_dir = File.basename(File.expand_path(File.join(File.dirname(__FILE__), '..')))
pwd = File.basename(File.expand_path(File.dirname(__FILE__)))
if parent_dir == PROJECT_NAME
  print("#{PROJECT_NAME} is already installed.")
  exit
end

# Copy all of the files into borg/pwd
`git clone https://github.com/Syncroness-Inc/borg.git`
FileUtils.mkdir_p("#{PROJECT_NAME}/#{pwd}")
Dir.foreach(".") do |f|
  FileUtils.mv(f, "#{PROJECT_NAME}/#{pwd}", :verbose => true) if f != PROJECT_NAME && f != "." && f != ".."
end

require "./borg/borglib.rb"

BorgLib.set_config_file_location("#{pwd}/config/borg_config.yaml")
#Ignore the new directory for the borg project, but only on this local install
File.write("borg/.git/info/exclude", "\n#{pwd}")
