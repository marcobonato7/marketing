const tc = require('@shopify/theme-check-node');
(async () => { const res = await tc.themeCheckRun(process.argv[2], undefined, () => {}); const offenses = res.offenses || res; const by = {};
  for (const o of offenses) { const k = (o.severity === 0 ? 'ERR ' : 'WARN ') + o.check + ' ' + (o.uri || '').split('/').slice(-2).join('/') + ' ' + o.message; by[k] = (by[k] || 0) + 1; }
  console.log(JSON.stringify(by, null, 1)); })();
