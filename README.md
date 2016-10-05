# jmessage-server
Source for JMessage Docker server

To build and run Docker containers locally:

1. Install [Docker](https://docs.docker.com/engine/getstarted/step_one/) for your platform.

2. Build the image: `./build.sh` 
	+ **NOTE**: this may take several minutes to build initially.

3. Run the container: `./run.sh`

4. To test with the jmessage-client (reference implementation) against a public server, do the following:

	`java -jar jmessage.jar -s jmessage.server.isi.jhu.edu -p 80 -a <client-username>`
