# Protocol

## Principle

The car's media unit uses RFCOMM plus a proprietary protocol to tunnel traffic to the media unit's HTTP server. This application provides a proxy and implements the protocol.

The protocol sends segments, kind of similarly to a TCP segment, consisting of a very simple header and data.


## Segment types

- TRANSMIT
- OPEN
- CLOSE
- HEARTBEAT


### OPEN

To establish a connection, the phone sends e.g.

| origin port | flags | destination |
|-------------|-------|-------------|
|       c0 e1 |    01 |       50 00 |

where `c0 e1` is little endian for the source port, `01` the flag for establishing a connection and `50 00` little endian for port 80.


### TRANSMIT

To transmit via an open connection, one entity may use

| origin port | flags | length | data                      |
|-------------|-------|--------|---------------------------|
|       c0 e1 |    00 |  98 00 | `GET /car/info/vin [...]` |

where `00` for the flags implies data transmission on an open connection.

The other sides response is similarly shaped,

| origin port | flags | length | data                      |
|-------------|-------|--------|---------------------------|
|       c0 e1 |    00 |  cb 00 | `HTTP/1.1 200 OK [...]`   |

again identify the origin port of the open connection to ensure that the traffic can be assigned correctly.

### CLOSE

To close a connection, the phone may issue

| origin port | flags |
|-------------|-------|
|       c0 e1 |    02 |

which the car responds to with the same segment for acknowledgement.


### HEARTBEAT

The car periodically sends a HEARTBEAT message, reading `00 00 03`.
If the phone encounters such message, it is returned.