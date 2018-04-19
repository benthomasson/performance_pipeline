
var angular = require('angular');
var util = require('./util.js');

var PerformancePipelineController = function($scope, $document, $location, $window) {

    window.scope = $scope;

    $scope.history = [];
    $scope.history_pairs = [];

    $scope.frame_dimensions = {'width': window.innerWidth,
                               'height': window.innerHeight};

    $scope.socket = io();

    $scope.socket.on('log', function (message) {
        console.log(["log", message]);
    });

    $scope.socket.on('CpuUsage', function (message) {
        console.log(["CpuUsage", message]);
        var percent = message / 100.0;
        if (percent !== undefined ) {
            $scope.needle.new_rotation = Math.max(Math.min(1.0, percent), 0.0) * 180;
            if ($scope.history.length > 0) {
                $scope.history_pairs.push([$scope.history.slice(-1)[0], percent]);
                $scope.history_pairs = $scope.history_pairs.slice(-30);
            }
            $scope.history.push(percent);
            $scope.history = $scope.history.slice(-31);
        }
    });

    $scope.describeArc = util.describeArc;

    $scope.needle = {'rotation': 0,
                     'new_rotation': 0};

    //60fps ~ 17ms delay
    setInterval(function () {
        if ($scope.needle.rotation > $scope.needle.new_rotation) {
            $scope.needle.rotation -= 1;
        }
        if ($scope.needle.rotation < $scope.needle.new_rotation) {
            $scope.needle.rotation += 1;
        }
        $scope.frame = Math.floor(window.performance.now());
        $scope.$apply();
    }, 17);

    console.log("Started performance_pipeline controller");
};
exports.PerformancePipelineController = PerformancePipelineController;
console.log("Loaded performance_pipeline controller");
