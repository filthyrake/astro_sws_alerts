Designed specifically with the JTW Astronomy GTR mount in mind, but this SHOULD work with pretty much any OnStepX mount running SWS.

This is NOT a complicated/fancy script - it just scrapes the SWS web interface and looks for keywords in the motor statuses and sends a text message alerting the user as appropriate.  I developed it as an easy way to detect/get notified about collisions.

Full installation instructions coming, but the short version is you run this as a Cron job or lambda or something to just regularly check the interface.  There are almost certainly better ways to solve this, but it works.
