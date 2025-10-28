Commands
--------
  host [--ttl SECONDS] [--port PORT]
  join <room-id>
  exit

Room ID format
--------------
  <token>@<ip>:<port>

  Host (A)                             Guest (B)
---------                            ---------
Generate token + listen              Parse room_id + connect
Display room ID                      Connect to host

   <--- handshake messages (Step 5) --->

Derived shared session key (later)
Start message loop
   <--- encrypted chat --->

TTL expires or exit
Connection closed, memory wiped
