
var angular = require('angular');
var PerformancePipelineController = require('./performance_pipeline.controller.js');
var ui_router = require('angular-ui-router');

var performance_pipeline = angular.module('performance_pipeline', ['ui.router']);
var performancePipeline = require('./performance_pipeline.directive.js');

performance_pipeline.config(function ($stateProvider, $urlRouterProvider) {

    $urlRouterProvider.otherwise('/index');

    $stateProvider
        .state({
            name: 'index',
            url: '/index',
            template: '<performance-pipeline></performance-pipeline>'
        });
});

performance_pipeline.controller('PerformancePipelineController', PerformancePipelineController.PerformancePipelineController);
performance_pipeline.directive('performancePipeline', performancePipeline.performancePipeline);

exports.performance_pipeline = performance_pipeline;
exports.ui_router = ui_router;
