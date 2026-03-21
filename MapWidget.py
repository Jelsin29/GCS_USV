import io
import sys

import folium
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6 import QtWebEngineWidgets
from folium.plugins import MousePosition
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication, QPushButton

import base64

# Make Icon
from PIL import Image


def image_to_base64(image_path, size=(100, 100)):
    try:
        with Image.open(image_path) as img:
            img = img.resize(size)
            if img.mode == "RGBA":
                img = img.convert("RGB")
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return ""


def icon_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except Exception as e:
        print(f"Error loading icon {image_path}: {e}")
        return ""


usv_icon_base64 = icon_to_base64("uifolder/assets/icons/usv.png")
target_marker_base64 = icon_to_base64("uifolder/assets/icons/target.png")
home_icon_base64 = icon_to_base64("uifolder/assets/icons/antenna.png")


class MapWidget(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, center_coord, starting_zoom=13):
        super().__init__()
        self.mission: list = []
        MapWidget.marker_coord = center_coord
        self.fmap = folium.Map(location=center_coord, zoom_start=starting_zoom)

        # Show mouse position in bottom right
        MousePosition().add_to(self.fmap)

        # store the map to a file
        data = io.BytesIO()
        self.fmap.save("map.html")
        self.fmap.save(data, close_file=False)

        # reading the folium file
        html = data.getvalue().decode()

        # find variable names
        self.map_variable_name = self.find_variable_name(html, "map_")

        # determine scripts indices
        endi = html.rfind("</script>")

        # inject code
        html = html[: endi - 1] + self.custom_code(self.map_variable_name) + html[endi:]
        data.seek(0)
        data.write(html.encode())

        # To Get Java Script Console Messages
        self.map_page = self.WebEnginePage(map_widget=self)
        self.setPage(self.map_page)

        # To Display the Map
        self.resize(800, 600)
        self.setHtml(data.getvalue().decode())

        # Add buttons
        self.btn_AllocateWidget = QPushButton(
            icon=QIcon("uifolder/assets/icons/16x16/cil-arrow-top.png"), parent=self
        )
        self.btn_AllocateWidget.setCursor(Qt.PointingHandCursor)
        self.btn_AllocateWidget.setStyleSheet("background-color: rgb(44, 49, 60);")
        self.btn_AllocateWidget.resize(25, 25)

        # A variable that holds if the widget is child of the main window or not
        self.isAttached = True

        # self.loadFinished.connect(self.onLoadFinished)

    def resizeEvent(self, event):
        self.btn_AllocateWidget.move(self.width() - self.btn_AllocateWidget.width(), 0)
        super().resizeEvent(event)

    class WebEnginePage(QWebEnginePage):
        def __init__(self, map_widget=None):
            super().__init__()
            self.markers_pos = []
            self._map_widget = map_widget

        def javaScriptConsoleMessage(self, level, msg, line, sourceID):
            if msg and msg[0] == "m" and self._map_widget is not None:
                self._map_widget.mission = []
                pairs = msg[1:].split("&")
                for pair in pairs:
                    self._map_widget.mission.append(list(map(float, pair.split(","))))
                print("mission: ", self._map_widget.mission)
            else:
                self.markers_pos = msg.split(",")
                print(msg)

    def find_variable_name(self, html, name_start):
        variable_pattern = "var "
        pattern = variable_pattern + name_start

        starting_index = html.find(pattern) + len(variable_pattern)
        tmp_html = html[starting_index:]
        ending_index = tmp_html.find(" =") + starting_index

        return html[starting_index:ending_index]

    def custom_code(self, map_variable_name):
        return """
            // custom code
            
            // Rotated Marker Function (unchanged)
            (function() {
                var proto_initIcon = L.Marker.prototype._initIcon;
                var proto_setPos = L.Marker.prototype._setPos;
                var oldIE = (L.DomUtil.TRANSFORM === 'msTransform');
                L.Marker.addInitHook(function () {
                    var iconOptions = this.options.icon && this.options.icon.options;
                    var iconAnchor = iconOptions && this.options.icon.options.iconAnchor;
                    if (iconAnchor) {
                        iconAnchor = (iconAnchor[0] + 'px ' + iconAnchor[1] + 'px');
                    }
                    this.options.rotationOrigin = this.options.rotationOrigin || iconAnchor || 'center bottom' ;
                    this.options.rotationAngle = this.options.rotationAngle || 0;
                    this.on('drag', function(e) { e.target._applyRotation(); });
                });
                L.Marker.include({
                    _initIcon: function() { proto_initIcon.call(this); },
                    _setPos: function (pos) { proto_setPos.call(this, pos); this._applyRotation(); },
                    _applyRotation: function () {
                        if(this.options.rotationAngle) {
                            this._icon.style[L.DomUtil.TRANSFORM+'Origin'] = this.options.rotationOrigin;
                            if(oldIE) { this._icon.style[L.DomUtil.TRANSFORM] = 'rotate(' + this.options.rotationAngle + 'deg)'; } 
                            else { this._icon.style[L.DomUtil.TRANSFORM] += ' rotateZ(' + this.options.rotationAngle + 'deg)'; }
                        }
                    },
                    setRotationAngle: function(angle) { this.options.rotationAngle = angle; this.update(); return this; },
                    setRotationOrigin: function(origin) { this.options.rotationOrigin = origin; this.update(); return this; }
                });
            })();
            
            var map = %s;
            
            var usvIcon = L.icon({ iconUrl: 'data:image/png;base64,%s', iconSize: [40, 40], });
            var targetIcon = L.icon({ iconUrl: 'data:image/png;base64,%s', iconSize: [40, 40], });
            var userIcon = L.icon({ iconUrl: 'data:image/png;base64,%s', iconSize: [40, 40], });
            var homeIcon = L.icon({ iconUrl: 'data:image/png;base64,%s', iconSize: [40, 40], });
                
            var mymarker = L.marker([%f, %f], {});  // Not added to map until user clicks in Marker Mode

            function moveMarkerByClick(e) {
                if (!mymarker._map) mymarker.addTo(map);
                mymarker.setLatLng([e.latlng.lat, e.latlng.lng]);
            }
            
            function undoWaypoint() {
                if(waypoints.length > 0) waypoints.pop().remove();
                if(lines.length > 0) lines.pop().remove();
            }
            
            var waypoints = [];
            var lines = [];
            function putWaypointEvent(e) {
                putWaypoint(e.latlng.lat.toFixed(4), e.latlng.lng.toFixed(4));
            }
            
            function putWaypoint(lat, lng) {
                var marker = L.marker([lat, lng], {}).addTo(map);
                if(waypoints.length > 0) {
                    points = [waypoints[waypoints.length-1].getLatLng(), marker.getLatLng()];
                    line = L.polyline(points, {color: 'red'}).addTo(map);
                    lines.push(line);
                }
                waypoints.push(marker);
            }
            
            var rect = 0;
            var corners = [];
            function drawRectangle(e) {
                if (corners.length < 2) {
                    corners.push(e.latlng);
                    if (corners.length == 2) {
                        if (rect) map.removeLayer(rect);
                        rect = L.rectangle(corners, {color: "#ff7800", weight: 1}).addTo(map);
                    }
                } else {
                    corners = [e.latlng];
                    if (rect) map.removeLayer(rect);
                }
            }
            
            // *** MODIFIED FUNCTION ***
            // This function now RETURNS the mission string instead of logging it.
            function setMission(mission_type) {
                var msg = "";
                if (mission_type == 1){ // waypoints
                    for(let i = 0; i < waypoints.length; i++){
                        msg += waypoints[i].getLatLng().lat.toFixed(4) + "," + waypoints[i].getLatLng().lng.toFixed(4);
                        if (i < waypoints.length - 1) {
                            msg += "&";
                        }
                    }
                } else { // exploration
                    if (corners.length == 2) {
                        for(let i = 0; i < 2; i++){
                            msg += corners[i].lat.toFixed(4) + "," + corners[i].lng.toFixed(4);
                            if (i < corners.length - 1) {
                                msg += "&";
                            }
                        }
                    }
                }
                return msg; // Return the data
            }
            
            function getMarkerPosition() {
                if (!mymarker._map) return null;
                var latlng = mymarker.getLatLng();
                return latlng.lat.toFixed(6) + "," + latlng.lng.toFixed(6);
            }

            function clearAll() {
                waypoints.forEach(marker => marker.remove());
                waypoints = [];
                lines.forEach(line => line.remove());
                lines = [];
                if (rect != 0) map.removeLayer(rect);
                corners = [];
                if (mymarker._map) map.removeLayer(mymarker);
            }

            map.on('click', putWaypointEvent);
            
            // end custom code
    """ % (
            map_variable_name,
            usv_icon_base64,
            target_marker_base64,
            home_icon_base64,
            home_icon_base64,
            self.marker_coord[0],
            self.marker_coord[1],
        )


if __name__ == "__main__":
    # create variables
    uskudar = [41.037083, 29.029528]

    # Display the Window
    app = QApplication([])
    widget = MapWidget(uskudar)
    widget.show()

    sys.exit(app.exec())
