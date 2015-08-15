Promise.longStackTraces();

;(function (win, doc, has, $, _, ol, undefined) {
  var fdr = {
    __VERSION__: 'dev',
    ANIM_DEFAULT_DURATION: 300,
    ANIM_DEFAULT_EASING: 'easeInExpo',
    ANIM_DEFAULT_EASING_IN: 'easeInExpo',
    ANIM_DEFAULT_EASING_OUT: 'easeOutExpo',
    MAP_DEFAULT_CENTER_LATLONG: [37.7577, -122.4376],
    MAP_DEFAULT_MAX_ZOOM: 18,
    MAP_DEFAULT_MIN_ZOOM: 13,
    MAP_DEFAULT_ZOOM: 15,
    MAP_SF_MAX_LAT: 37.832371,
    MAP_SF_MAX_LONG: -122.354874,
    MAP_SF_MIN_LAT: 37.604031,
    MAP_SF_MIN_LONG: -123.013657,
    PROP_OPACITY_LIGHT: 0.25,
    PROP_OPACITY_MED: 0.5,
    PROP_OPACITY_DARK: 0.75,
    TIMEOUT_DEBOUNCE_MAXWAIT: 2500,
    TIMEOUT_INPUT_KEYPRESS: 500,
    TMPL_URL_FOODER_API: _.template('/api/${Fooder.__VERSION__}${uri}'),
    TMPL_URL_LOCATION_SEARCH: _.template('//nominatim.openstreetmap.org/search?format=json&countrycodes=us&bounded=1&limit=10&q=${query}'),
    TMPL_URL_REVERSE_GEOCODE: _.template('//nominatim.openstreetmap.org/reverse?format=json&zoom=${zoom}&addressdetails=1&lat=${lat}&lon=${long}'),
    mixins: {},
    ui: {},
  };


  fdr.location = {
    address: {
      full: undefined,
      house: undefined,
      street: undefined,
      city: undefined,
      state: undefined,
      postal: undefined,
      country: undefined,
    },

    coords: {
      latitude: 0.0,
      longitude: 0.0,
    },

    detect: function () {
      return new Promise(function (resolve, reject) {
        navigator.geolocation.getCurrentPosition(function (geo) {
          if (fdr.location.outsideServiceArea(geo.coords.latitude, geo.coords.longitude)) {
            return reject();
          }

          fdr.location.set({
            coords: {
              latitude: parseFloat(geo.coords.latitude),
              longitude: parseFloat(geo.coords.longitude),
            },
          });

          resolve(fdr.location);
        }, reject);
      });
    },

    set: function (opts, nopersist) {
      if (!opts) {
        return;
      }

      if (opts.location && fdr.location.outsideServiceArea(opts.location.latitude, opts.location.longitude)) {
        return;
      }

      if (opts.address) {
        for (var p in fdr.location.address) {
          if (p in opts.address && opts.address[p]) {
            fdr.location.address[p] = opts.address[p]

            if (!nopersist) {
              fdr.storage.set('location.address.' + p, fdr.location.address[p]);
            }
          }
        }
      }

      if (opts.coords) {
        for (var p in fdr.location.coords) {
          if (p in opts.coords && opts.coords[p]) {
            fdr.location.coords[p] = parseFloat(opts.coords[p]);

            if (!nopersist) {
              fdr.storage.set('location.coords.' + p, fdr.location.coords[p])
            }
          }
        }
      }
    },

    load: function () {
      return new Promise(function (resolve, reject) {
        if (!fdr.location.hasCoords()) {
          fdr.location.set({
            coords: {
              latitude: fdr.storage.get('location.coords.latitude'),
              longitude: fdr.storage.get('location.coords.longitude')
            },
          });
        }

        if (!fdr.location.hasAddr()) {
          fdr.location.set({
            address: {
              house: fdr.storage.get('location.address.house'),
              street: fdr.storage.get('location.address.street'),
              city: fdr.storage.get('location.address.city'),
              state: fdr.storage.get('location.address.state'),
              postal: fdr.storage.get('location.address.postal'),
              country: fdr.storage.get('location.address.country'),
            },
          });
        }

        return fdr.location.hasCoords() ?
          resolve(fdr.location) :
          reject('no stored or in-memory location data');
      });
    },

    hasCoords: function () {
      return fdr.location.coords.latitude && fdr.location.coords.longitude;
    },

    hasAddr: function () {
      return fdr.location.address.city && fdr.location.address.state;
    },

    outsideServiceArea: function (lat, long) {
      if (
        lat < fdr.MAP_SF_MIN_LAT ||
        lat > fdr.MAP_SF_MAX_LAT ||
        long < fdr.MAP_SF_MIN_LONG ||
        long > fdr.MAP_SF_MAX_LONG
      ) {
        return true;
      } else {
        return false;
      }
    },
  };


  fdr.storage = {
    get: function (key, def) {
      return has.localstorage ? (localStorage.getItem(key) || def) : def;
    },

    set: function (key, val) {
      if (has.localstorage) {
        localStorage.setItem(key, val);
      }

      return val;
    },
  };


  fdr.ui._mixins = {
    active: false,
    show: function () {
      this.active = true;
      this.$el.removeClass('hidden').trigger('show');
    },
    hide: function () {
      this.active = false;
      this.$el.addClass('hidden').trigger('hide');
    },
  };


  fdr.ui.map = new (function Map () {
    _.extend(this, fdr.ui._mixins);
    this.$el = $('#mapContainer');

    this.getView = function (lat, long) {
      return new ol.View({
        center: ol.proj.transform([long, lat], 'EPSG:4326', 'EPSG:3857'),
        maxZoom: fdr.MAP_DEFAULT_MAX_ZOOM,
        minZoom: fdr.MAP_DEFAULT_MIN_ZOOM,
        zoom: fdr.MAP_DEFAULT_ZOOM,
      });
    };

    this.getIcon = function(lat, long, opts) {
      var feature,
          style,
          source,
          layer;

      feature = new ol.Feature(_.extend({
        geometry: new ol.geom.Point(ol.proj.transform([long, lat], 'EPSG:4326', 'EPSG:3857')),
      }, opts));

      style = new ol.style.Style({
        image: new ol.style.Icon({
          anchor: [0.5, 0.5],
          anchorXUnits: 'fraction',
          anchorYUnits: 'fraction',
          opacity: 1.0,
          scale: 1.0,
          src: '/img/icon-truck-16x16.png',
          size: [16, 16],
        }),
      });
      feature.setStyle(style);

      source = new ol.source.Vector({
        features: [feature],
      });

      layer = new ol.layer.Vector({
        source: source,
      });

      return layer;
    };

    this.addIcon = function (lat, long, opts) {
      if (!this.map) {
        return;
      }

      this.map.addLayer(this.getIcon(lat, long, opts));
    };

    this.center = function (lat, long) {
      this.view.setCenter(ol.proj.transform([long, lat], 'EPSG:4326', 'EPSG:3857'));
    };

    this.popups = function () {
      var $popup = $('#popup'),
          $body = $('body'),
          mapel;

      if (!$popup.length) {
        $popup = $('<div>').attr({ id: 'popup' }).appendTo($body);
      }

      mapel = new ol.Overlay({ element: $popup[0], positioning: 'bottom-center', stopEvent: false }),
      this.map.addOverlay(mapel);

      this.map.on('click', function (e) {
        var feature = fdr.ui.map.map.forEachFeatureAtPixel(e.pixel,
            function(feature, layer) {
              return feature;
            });
        if (feature) {
          mapel.setPosition(e.coordinate);
          $popup.popover({
            'placement': 'top',
            'html': true,
            'content': '<div style="width:200px;">' +
              '<strong>' + feature.get('name') + '</strong><br />' +
              '<span>' + feature.get('address') + '</span><br />' +
              '<small>Between ' + feature.get('border_streets') + '</small><br />' +
              '<small>- ' + feature.get('menu').split(',').join('<br /> - ') + '</small>' +
              '</div>',
          });
          $popup.popover('show');
        } else {
          $popup.popover('destroy');
        }
      });

      this.map.on('pointermove', function(e) {
        if (e.dragging) {
          $popup.popover('destroy');
          return;
        }
        var pixel = fdr.ui.map.map.getEventPixel(e.originalEvent);
        var hit = fdr.ui.map.map.hasFeatureAtPixel(pixel);
        var tgt = fdr.ui.map.map.getTarget();

        if (tgt && tgt.style) {
          tgt.style.cursor = hit ? 'pointer' : '';
        }
      });
    };

    this.init = function (lat, long) {
      this.view = this.getView(lat, long);
      this.map = window._olmap = new ol.Map({
        layers: [new ol.layer.Tile({ source: new ol.source.OSM() })],
        target: this.$el.attr('id') || 'map',
        controls: ol.control.defaults({
          attributionOptions: { collapsible: true }
        }),
        view: this.view,
      });
      this.popups();
    };

    $.getJSON('/api/dev/vendors').done(function (vendors) {
      _.forEach(vendors, function (vendor) {
        var lat = parseFloat(vendor.latitude),
            long = parseFloat(vendor.longitude);
        setTimeout(function() {
          fdr.ui.map.addIcon(parseFloat(vendor.latitude), parseFloat(vendor.longitude), vendor);
        }, 0);
      });
    });
  });


  fdr.ui.dither = new (function Dither () {
    _.extend(this, fdr.ui._mixins);
    this.$el = $('#dither');
  });


  fdr.ui.search = new (function Search () {
    _.extend(this, fdr.ui._mixins);
    this.$el = $('#search'),
    this.$input = $('#searchInput');
    this.$glbl = $('body').add($(window));

    this.toggle = function (showOnly, hideOnly) {
      if ((showOnly && fdr.ui.search.active) || (hideOnly && !fdr.ui.search.active)) {
        return;
      }

      fdr.ui.search.activated = true;
      fdr.ui.search.active = !fdr.ui.search.active;
      fdr.ui.search.$el.fadeToggle('slow');
    };

    this.$glbl.off('keydown.search.toggle').on('keydown.search.toggle', function (e) {
      if (!e || (e.which || e.keyCode) !== 27) {
        return;
      }

      e.stopPropagation();
      fdr.ui.search.$input[fdr.ui.search.active ? 'blur' : 'focus']();
      fdr.ui.search.toggle(!fdr.ui.search.active, fdr.ui.search.active);
    });

    // this.naiveGeoFilter = function (results) {
    //   return _.filter(results || [], function (res) {
    //     return !fdr.location.outsideServiceArea(parseFloat(res.lat), parseFloat(res.lon));
    //   });
    // };

    var ostreets = new Bloodhound({
      datumTokenizer: function (loc) { return Bloodhound.tokenizers.whitespace(loc.display_name); },
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      remote: {
        url: fdr.TMPL_URL_LOCATION_SEARCH({ query: '%QUERY' }),
        wildcard: '%QUERY',
      }
    });

    this.$input
      .off('keypress.search keydown.search keyup.search')
      .on('keypress.search keydown.search keyup.search',
    function (e) {
      if (!e) {
        return;
      }

      e.stopPropagation();
      if ((e.which || e.keyCode) === 27) {
        fdr.ui.search.$el.blur();
        fdr.ui.search.toggle(false, true);
      }
    });

    this.$input.typeahead({
      hint: true,
      highlight: true,
      minLength: 3
    }, {
      name: 'Locations',
      displayKey: 'display_name',
      source: ostreets,
      // source: function (query, cb) {
      //   ostreets.get(query, function(suggestions) {
      //     cb(fdr.ui.search.naiveGeoFilter(suggestions));
      //   });
      // },
    }).bind('typeahead:select', function(e, suggestion) {
      fdr.ui.map.center(parseFloat(suggestion.lat), parseFloat(suggestion.lon));
      fdr.ui.search.toggle();
    });
  });


  fdr.ui.splash = new (function Splash () {
    _.extend(this, fdr.ui._mixins);
    this.$el = $('#splash');
    this.$btn = $('a.btn-primary', this.$el);
    this.$btn.off('click.splash').on('click.splash', function (e) {
      this.hide();

      fdr.location.detect().then(function (loc) {
        fdr.ui.map.center(loc.coords.latitude, loc.coords.longitude);
      }).catch(function (e) {
        fdr.ui.search.$el.css({ display: 'none' }).removeClass('hidden');
        fdr.ui.search.toggle(true);
      });
    }.bind(this));

    this.hide = function () {
      this.$el.remove();
      fdr.ui.dither.hide();
    }
  });


  fdr.init = function() {
    fdr.location.load().catch(function (e) {
      fdr.ui.splash.show();
      fdr.ui.dither.show();
    }).then(function () {
      fdr.ui.map.init.apply(fdr.ui.map,
        fdr.location.hasCoords() ?
          [fdr.location.coords.latitude, fdr.location.coords.longitude] :
          fdr.MAP_DEFAULT_CENTER_LATLONG
      );
    });
  };

  fdr.init();
})(window, document, Modernizr, jQuery.noConflict(), _, window.ol);
