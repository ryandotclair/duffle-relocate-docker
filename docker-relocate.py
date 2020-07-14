import os
import json
# Reason:
# Duffle can time out with large images (especially for Tanzu Build Service). This script uses a local registry /
# temporarily and uses docker-cli to push images in (which doesn't time out).

# Instructions:
# Requires Docker installed. Update the "new_reg" varisable below with the name of the registry you want this sent to
# And update the "build_file_name" variable with the file duffle uses.
# Run this script in same folder as duffle and the build-service file.
# End result is containers sent to the registry and a new relocate file called "relocated_new.json"

new_reg = "harbor.sgrhas.local/library"
build_file_name = "build-service-0.2.0.tgz"

print ("spinning up a temporary registry docker container")
os.system("docker run -d --rm -p 5333:5000 --name temp-reg registry")
images = os.popen("./duffle relocate -f ./" + build_file_name + " -m ./relocated.json -p localhost:5333 -v | awk '{print $4}'").read().split('\n')
new_list = []
print (images)

for i in images:
    try:
        print ("About to pull " + i)
        os.system("docker pull " + i)
    except:
        print ("there was an issue with " + i)
        pass
print("////Now doing a tag + push////")

image_hash = os.popen("docker images | grep localhost:5000")

for i in image_hash:
    print ("parsing " + i)
    line = " ".join(i.split())
    old_hashid = line.split(" ")[2]
    old_name = line.split(" ")[0]
    new_name = new_reg + old_name[14:]
    print ("existing image name:  " + old_hashid)
    print ("new image name:  " + new_name)
    print ("runnning: docker tag " + old_hashid + " " + new_name)
    os.system ("docker tag " + old_hashid + " " + new_name)
    print ("running: docker push " + new_name)
    os.system ("docker push " + new_name)
    new_list.append(new_name)
print ("Killing the registry")
os.system("docker stop temp-reg")

print ("Updating the relocate file.")
with open('./relocated.json') as f:
    data = json.load(f)
    print (data)
    for i in data:
        print ("key: " + i)
        print ("Value: " + data[i])
        data[i] = new_reg + data[i][14:]
        print ("New Value: " + data[i])
    print ("done")
    print (data)

with open("./relocated_new.json", "w+") as f:
    f.write (json.dumps(data))
print ("Here's the new file!")
os.system("cat ./relocate_new.json")
