const Bacnet = require('bacstack');

const client = new Bacnet({
  apduTimeout: 10000,
  interface: '192.168.1.105'
});

const OBJECT_TYPE_NAMES = {
  0: 'ANALOG_INPUT',
  1: 'ANALOG_OUTPUT',
  2: 'ANALOG_VALUE',
  3: 'BINARY_INPUT',
  4: 'BINARY_OUTPUT',
  5: 'BINARY_VALUE',
  8: 'DEVICE'
};

function getObjectTypeName(typeId) {
  return OBJECT_TYPE_NAMES[typeId] || `UnknownObjectType(${typeId})`;
}

// Helper to read multiple properties individually
function readPropertiesOneByOne(address, objectId, propertyIds, callback) {
  const results = {};
  let remaining = propertyIds.length;

  propertyIds.forEach((propId) => {
    client.readProperty(address, objectId, propId, (err, value) => {
      if (err) {
        results[propId] = { error: err.message };
      } else {
        // The property value is typically in `value.values[0].value`
        results[propId] = value?.values?.[0]?.value;
      }
      remaining -= 1;
      if (remaining === 0) {
        callback(null, results);
      }
    });
  });
}

// When a device responds with I-Am:
client.on('iAm', (device) => {
  console.log('====================================================');
  console.log('Discovered device:');
  console.log(`  Address:       ${device.address}`);
  console.log(`  Device ID:     ${device.deviceId}`);
  console.log(`  Max APDU:      ${device.maxApdu}`);
  console.log(`  Segmentation:  ${device.segmentation}`);
  console.log(`  Vendor ID:     ${device.vendorId}`);
  console.log('====================================================\n');

  // Read the device's OBJECT_LIST
  client.readProperty(
    device.address,
    { type: Bacnet.enum.ObjectType.DEVICE, instance: device.deviceId },
    Bacnet.enum.PropertyIdentifier.OBJECT_LIST,
    (err, result) => {
      if (err) {
        console.error('Error reading OBJECT_LIST:', err);
        return;
      }

      const objectListEntries = result.values;
      console.log('OBJECT_LIST returned the following entries:\n');
      console.log(JSON.stringify(objectListEntries, null, 2));
      console.log('');

      // For each object, read properties individually
      objectListEntries.forEach((entry) => {
        const obj = entry.value; // { type, instance }
        const typeName = getObjectTypeName(obj.type);

        // Skip the device object
        if (obj.type === 8) {
          console.log(`-- Skipping DEVICE object (type=${typeName}, instance=${obj.instance})\n`);
          return;
        }

        console.log(`-- Reading properties for: type=${typeName}, instance=${obj.instance}`);

        // Which properties do we want?
        const propertiesToRead = [
          Bacnet.enum.PropertyIdentifier.OBJECT_NAME,    // 77
          Bacnet.enum.PropertyIdentifier.DESCRIPTION,    // 28
          Bacnet.enum.PropertyIdentifier.UNITS,          // 117
          Bacnet.enum.PropertyIdentifier.PRESENT_VALUE,  // 85
        ];

        // Read them one by one
        readPropertiesOneByOne(device.address, { type: obj.type, instance: obj.instance }, propertiesToRead, (err, values) => {
          if (err) {
            console.error(`Error: ${err}`);
            return;
          }

          // Extract the values
          const objectName = values[Bacnet.enum.PropertyIdentifier.OBJECT_NAME] || 'Unknown';
          const description = values[Bacnet.enum.PropertyIdentifier.DESCRIPTION] || 'N/A';
          const unitsCode = values[Bacnet.enum.PropertyIdentifier.UNITS];
          const presentValue = values[Bacnet.enum.PropertyIdentifier.PRESENT_VALUE];

          // Convert units code to a friendly name if it's numeric
          let units = 'N/A';
          if (typeof unitsCode === 'number') {
            // Try to map using bacstack’s enum
            units = Bacnet.enum.EngineeringUnits[unitsCode] || `UnknownUnits(${unitsCode})`;
          } else if (typeof unitsCode === 'string') {
            units = unitsCode;
          }

          console.log(`   OBJECT_NAME:   ${objectName}`);
          console.log(`   DESCRIPTION:   ${description}`);
          console.log(`   UNITS:         ${units}`);
          console.log(`   PRESENT_VALUE: ${JSON.stringify(presentValue)}`);
          console.log('');
        });
      });
    }
  );
});

// Broadcast a Who-Is to discover devices
client.whoIs();
