# Custom Netcat

This script is an attempt to mimic Netcat. It's an abstraction of the must-used functionalities of the tool but in a limited way. The foundational component in the script is the use of sockets for the client-server interaction and how to receive and send commands and responses respectively.

Netcat is an arbitrary tool for performing pen-testing activities and way more. Sockets, in general, present a completely different approach for software, many of them can be used in the security industry as well.

## The client

The client is conformed by an Ipv4 TCP socket module, which evaluates host and port values from the input args. So, we if have any data, it sends it, and an infinite while loop will receive and send the interaction until the connection is alive

## The server

The server does a little bit more, it checks and connects to a socket instance and it blocks the execution for incoming connections. When a connection is established, a new execution thread is created for that connection.

In both scenarios, the data collection is handled by limited socket buffers with encoded/decoded mechanisms

## How to use?

Because the nature of the program is to perform reverse shell connections. The server side is the one that triggers the complete connection to the client. The server can hold several instructions to trigger whenever the client is connected to it.

1. Executing bash commands: `python -l -e "ls -A" [Server] [PORT]`.

The `-l` flag is for listening, and the `-e` flag is for execution

2. Outputing results to a file: `python -l -o /tmp/file.out [Server] [PORT]`

You can later check the output content with the `cat`, `less`, or `more` commands

3. Running a shell command (not persistent): `python -l -c [Server] [PORT]`

The client-side is simpler.

Just run the same file without some arguments: `python netcat.py -l -c [Server] [PORT]`

## Credits

 - [David E Lares](https://twitter.com/davidlares3)

## License

 - [MIT](https://opensource.org/licenses/MIT)
