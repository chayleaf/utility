// ==UserScript==
// @name         Youtube Kusa Counter
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Display kusa graph for stream vods (activate from menu)
// @author       pavlukivan
// @match        https://www.youtube.com/watch?v=*
// @grant        GM_registerMenuCommand
// @require https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.9.3/Chart.min.js
// ==/UserScript==
var initData;
var parentWindow;
function getChat(callback, progressCb) {
    var ytInitialData = initData;
    var continuations = ytInitialData.contents.twoColumnWatchNextResults.conversationBar.liveChatRenderer.header.liveChatHeaderRenderer.viewSelector.sortFilterSubMenuRenderer.subMenuItems;
    if(!continuations) return;
    var continuation;
    for(var i in continuations)
        if(!continuations[i].selected)
            continuation = continuations[i];
    if(!continuation) continuations = continuations[0];
    continuation = continuation.continuation.reloadContinuationData.continuation;
    var allData = [];
    var fetched = {};
    function iter(frame) {
        if(!continuation) return callback(allData);
        if(!frame) {
            if(!fetched[continuation]) { //just a safety measure
                fetched[continuation] = true;
                let frame = document.createElement('iframe');
                frame.style = 'position: absolute;left: -10000px; top: 0px;';
                frame.src = 'https://www.youtube.com/live_chat_replay?continuation=' + continuation;
                frame.onload = function() { iter(frame); };
                document.body.appendChild(frame);
            } else {
                continuation = null;
                iter();
            }
        } else {
            continuation = null;
            while(true) {
                var ytInitialData = frame.contentWindow.ytInitialData;
                var actions = ytInitialData.continuationContents.liveChatContinuation.actions;
                if(actions == null) {
                    var initData2 = frame.contentWindow.document.body.innerHTML.split('window["ytInitialData"] = ')[1].split('\n')[0].trimEnd()
                    while(initData2.endsWith(';')) initData2 = initData2.substr(0, initData2.length - 1);
                    initData2 = eval('(function(){return ' + initData2 + '})()');
                    actions = initData2.continuationContents.liveChatContinuation.actions;
                }
                var lastTs;
                for(var i in actions) {
                    var actions2 = actions[i].replayChatItemAction;
                    if(!actions2 || !actions2.actions) continue;
                    for(var j in actions2.actions) {
                        var action = actions2.actions[j];
                        if(!action || !action.addChatItemAction) continue;
                        var item = action.addChatItemAction.item;
                        var renderer = item.liveChatTextMessageRenderer || item.liveChatPaidMessageRenderer;
                        if(!renderer || !renderer.message) continue;

                        var ts = actions2.videoOffsetTimeMsec;
                        var text = '';
                        for(var k in renderer.message.runs) {
                            var run = renderer.message.runs[k];
                            if(run.text) text += run.text;
                            else if(run.emoji) text += run.emoji.shortcuts[0];
                        }
                        lastTs = ts / 1000;
                        allData.push({ts: lastTs, text: text});
                    }
                }
                progressCb(lastTs);
                var continuations = ytInitialData.continuationContents.liveChatContinuation.continuations;
                if(!continuations || !continuations[0] || !continuations[0].liveChatReplayContinuationData || !continuations[0].liveChatReplayContinuationData.continuation) {
                    break;
                }
                continuation = continuations[0].liveChatReplayContinuationData.continuation;

                break;
            }
            document.body.removeChild(frame);
            iter();
        }
    }
    iter();
}

GM_registerMenuCommand('Display kusa graph from chat replay', (function start() {
    'use strict';
    var tmp = document.getElementById('primary-inner');
    parentWindow = window;
    initData = ytInitialData;
    if(!tmp) setTimeout(start, 500);
    var player = tmp.querySelector('#player');
    var progress = document.createElement('div');
    progress.style = "margin-top: 25px;text-align: center;";
    progress.className = "title style-scope ytd-video-primary-info-renderer";
    player.appendChild(progress);
    console.log('prog', progress);

    var canvas = document.createElement('canvas');
    var parent = document.createElement('div');
    parent.style = 'position: relative;margin-left: 20px;';
    parent.appendChild(canvas);
    let kusaVariants = ['草', 'ｗｗｗ', 'kusa', 'wwww', 'lol', 'lmao', 'lmfao', 'hahaha'];
    function cb(time) {
        var seconds = (''+Math.floor(time % 60)).padStart(2, '0');
        var minutes = (''+Math.floor((time / 60) % 60)).padStart(2, '0');
        var hours = (''+Math.floor((time / 3600) % 60)).padStart(2, '0');
        var timestr = hours + ':' + minutes + ':' + seconds;
        progress.innerText = 'Loading chat replay: ' + timestr;
    }
    getChat(function(allData) {
        progress.style = 'display: none';
        player.appendChild(parent);
        var kusas = [];
        var bc = [];

        for(var k in allData) {
            var minute = Math.floor(allData[k].ts / 60);
            while(kusas.length <= minute) kusas.push(0);
            let text = allData[k].text.toLowerCase();
            for(var y in kusaVariants) {
                if(text.indexOf(kusaVariants[y]) >= 0) {
                    kusas[minute] += 1;
                    break;
                }
            }
        }

        var data = [];

        for(var h in kusas) {
            if((h + 1 >= kusas.length || kusas[h + 1] != kusas[h]) || (h <= 0 || kusas[h - 1] != kusas[h]))
                data.push({
                    x: h,
                    y: kusas[h],
                });
        }
        Chart.defaults.global.elements.line.lineTension = 0;
        Chart.defaults.global.elements.line.borderColor = 'rgba(255, 0, 0, 1)';
        var myChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: [''],
                datasets: [
                    {
                        label: 'kusa count',
                        //borderColor: bc,
                        data: data//[{x:0,y:0},{x:0.333,y:5},{x:0.666,y:10},{x:1,y:20}]
                    }
                ]
            },
            options: {
                responsive: true,
                legend: {display: false},
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, data) {
                            var label = data.datasets[tooltipItem.datasetIndex].data[tooltipItem.index].x;
                            if (label) {
                                var minutes = (''+Math.floor(label % 60)).padStart(2, '0');
                                var hours = (''+Math.floor((label / 60) % 60)).padStart(2, '0');
                                label = hours + ':' + minutes + ':00';
                            }
                            return label;
                        },
                        title: function(tooltipItem, data) {
                            //console.log(tooltipItem, data);
                            var label = '' + (0 + data.datasets[tooltipItem[0].datasetIndex].data[tooltipItem[0].index].y);
                            return label;
                        },
                    }
                },
                scales: {
                    xAxes: [
                        {
                            type: 'linear',
                            display: true,
                            scaleLabel: {display: true},
                            ticks: {display: false}
                        }
                    ],
                    yAxes: [
                        {
                            ticks: {display: false}
                        }
                    ]
                }
            }
        });
    }, cb);
}));




