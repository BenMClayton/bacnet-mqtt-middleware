const Bacnet = require('bacstack');
const client = new Bacnet({
	apduTimeout: 10000,
	interface: '192.168.1.105', // Your local IP on the same subnet as YABE
  });
  

// Broadcast a Who-Is request so the simulator replies with I-Am
client.whoIs();

client.on('iAm', (device) => {
  console.log('Discovered device:', device);
  // Use the discovered device’s address (which should include the proper port)
  client.readProperty(
	'192.168.1.105:52123',
	{ type: Bacnet.enum.ObjectType.DEVICE, instance: 24 },
	Bacnet.enum.PropertyIdentifier.objectList,
	(err, value) => {
	  if (err) {
		console.error('Direct read error:', err);
	  } else {
		console.log('Object list:', JSON.stringify(value, null, 2));
	  }
	}
  );
  
});

// Close the client after 20 seconds
setTimeout(() => {
  client.close();
  console.log('Client closed.');
}, 20000);
