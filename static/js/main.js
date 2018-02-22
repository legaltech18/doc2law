jQuery(function($) {
    if ($("#map").length) {
        var map = window.map = L.map("map").setView(
            [52.51371369804256, 13.42460632324219],
            10
        );

        L.tileLayer("http://{s}.tile.osm.org/{z}/{x}/{y}.png", {
            attribution:
                '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // map.on('moveend', function () {
        //   console.log(map.getCenter());
        // });

        navigator.geolocation.getCurrentPosition(function(position) {
            jQuery(".logo--small").removeClass("loading");

            var currentPosition = [
                position.coords.latitude,
                position.coords.longitude
            ];

            map.setView(currentPosition);

            L.marker(currentPosition).addTo(map);

            if (window.renderMarkers) {
                window.renderMarkers(map);
            }
        });
    }

    $('button[type="submit"]').click(function() {
        $(".logo").addClass("loading");
    });
});
