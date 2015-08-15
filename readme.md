# Welcome to fooder!
**fooder** is a basic back- and front-end application that shows the location of food vendor trucks in San Francisco, optionally geolocating the user and allowing them to search for locations to find nearby trucks.

## Usage
Visit [fooder.mway.co](http://fooder.mway.co/).

## Notes
Some things of potential interest are:
- Uses clay!
- Bootstrapped almost entirely via configuration, including routing, resources, etc
- Includes an (optional) decorator factory for parameter/route reuse and meta-configuration for easier app development/API definition
- Module-level configuration wrapper with autonamespacing (for convenience)
- Data consumption from OpenSF/sfgov.org
- Parsing vendor data for saner representation
- Basic, by-default transactional batching via SQLAlchemy (e.g. deferred commits)
- Integration with OpenStreetMap.org via OpenLayers
- Geolocation (with lat/long bounding restrictions to keep autodetection to SF)
- Basic map use including markers, positioning, etc

## Roadmap / TODO
- [ ] Add vendor names and food items to local search data provider
- [ ] Include relative distances on vendors
- [ ] Backend result filtering based on either radius or route distance
- [ ] Autozoom on search results using the area of lat/long bounding box as a coefficient
- [ ] Use more intelligent distancing for constraining geolocation to SF; e.g., don't use a lat/long bounding box
- [ ] Introduce a beacon system; include native and SMS notifications to notify users when a truck is within a configurable proximity
- [ ] Parse table data within permit schedule PDFs for schedule info
- [ ] Prettier UI
