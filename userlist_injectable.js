console.log("Evaluating script for page");
var loadmore = document.querySelector('#watchers > button:nth-child(3)');
var numWatching = document.querySelector('#watchers '
                                         + 'div:nth-child(1) '
                                         + 'div:nth-child(2)').innerHTML;
numWatching = numWatching.split(" ")[0];
isK = numWatching.slice(-1);


if(isK == "K"){
    numWatching = numWatching.slice(0, numWatching.length - 1);
    numWatching = Number(numWatching) * 1000;
}

console.log("Setting Interval");
var killvalue = setInterval(function(){loadmore.click(); }, 1000);
var watcherList = 0;

console.log("Setting Timeout");
setTimeout(function(){
    clearInterval(killvalue);
    watcherList = document.querySelectorAll('#watchers ._2QMci');
    
    for(var i = 0; i < watcherList.length; i++){
        console.log("Printing WatcherList");
        console.log(watcherList[i].innerHTML);
    };     
}, 5000); // (1000*60*5)
