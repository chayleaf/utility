// ==UserScript==
// @name         Madoka ftw
// @namespace    *
// @version      0.1.6.2
// @description  Madoka ftw
// @author       pavlukivan
// @match        *://*/*
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_addValueChangeListener
// @grant        GM_registerMenuCommand
// @grant        GM_getResourceURL
// @resource     madokaFont https://github.com/pavlukivan/utility/raw/master/MadokaRunesPavlukivan-1.0.ttf
// ==/UserScript==

//config start
var archaic = GM_getValue('archaic', false);
var letterCount = GM_getValue('letterCount', 0); //count of letters to replace, ordered by usage frequency
var transformCyrillic = false;
var transformMonospaceFonts = false;

//config that you probably shouldn't change
var FONT = 'MadokaRunesPavlukivan';
var allToUpper = archaic;
var allToLower = !archaic;
var LIMIT_CHILDREN = 1000; //don't descend into elements if they have more than 1000 children
var styleContent = "font-family:" + FONT + "!important;font-weight:normal!important;padding:0px 0px!important;border:none!important;float:none!important;"; //runes are alread pretty bold, dont make them even bolder
var tagBlacklist = {"noscript":true, "script":true, "style":true, "title":true, "textarea":true, "text":true, "code":true};
var marker = "w17ch_k155"; //a random string used to mark stuff already affected by script
var markerGen = marker + "_g"; //marks generated divs/spans
var classBlacklist = {"CodeMirror":true, marker:true};
var lettersChildren = {'A':1, 'O':1, 'U':1, 'B':1}; //count of letters that should be activated along with these. Currently only zero/one is supported.
//config end

//       charset: 1234567890qwertyuiopasdfghjklzxcvbnmßüöä. English wikipedia is used for reference. Upper because 'ß'.toUpperCase() == 'SS', not 'ẞ'
//var charFreq = 'EAIOTNRSLDCUHMGPFYB0VW1K23549ZX687JQÜÄÖẞ';
var charFreq = 'EAÄIOÖTNRSLDCUÜHMGPFYBẞ0VW1K23549ZX687JQ'; //changed order of German letters

var lowFreq = charFreq.toLowerCase();


letterCount = Math.min(charFreq.length, letterCount);
GM_addStyle("@font-face { font-family:" + FONT + ";src:url('" + GM_getResourceURL('madokaFont') + "'); }");
var style = GM_addStyle('');
var helperStyle = GM_addStyle('');
var elId = 0;

var classesByFontFamily = {};

function setElementFontFamily(node, fontFamily, additions=null) {
    if(!additions) {
        additions = '';
    }
    fontFamily += additions;
    var className = classesByFontFamily[fontFamily];
    if(!className) {
        className = marker + '_' + elId++;
        helperStyle.innerText += '.' + className + '{font-family:' + fontFamily + '!important;}\n';
        classesByFontFamily[fontFamily] = className;
    }
    node.classList.add(className);
}

function updateStyle() {
    var content = styleContent;
    if(allToUpper) {
        content += ' text-transform: uppercase!important;'
    }
    if(allToLower) {
        content += ' text-transform: lowercase!important;'
    }
    style.innerText = ((letterCount == charFreq.length ? "*" : "." + marker) + " { " + content + " }");
}

function disableStyle() {
    style.innerText = '';
}

updateStyle();

//https://github.com/greybax/cyrillic-to-translit-js/blob/master/CyrillicToTranslit.js
const cyr2lat = {"а": "a","б": "b","в": "v","ґ": "g","г": "g","д": "d","е": "e","ё": "yo","є": "ye","ж": "j","з": "z","и": "i","і": "i","ї": "yi","й": "y","к": "k","л": "l","м": "m","н": "n","о": "o","п": "p","р": "r","с": "s","т": "t","у": "u","ф": "f","х": "h","ц": "c","ч": "ch","ш": "sh","щ": "sh'","ъ": "'","ы": "y","ь": "'","э": "e","ю": "yu","я": "ya",};
const cyr2latWordStart = {"е":"ye",};
//used for translating characters that arent available yet back to cyrillics (e.g. if y in ye isnt available, we show y as й and e as runes)
var lat2cyr = {"a":"а","b":"б","c":"ц","d":"д","e":"е","f":"ф","g":"г","h":"х","i":"и","j":"ж","k":"к","l":"л","m":"м","n":"н","o":"о","p":"п","q":"к","r":"р","s":"с","t":"т","u":"у","v":"в","w":"в","x":"з","y":"й","z":"з","'":"ь"};

function shouldRunify(input) {
    if(letterCount == charFreq.length) { //everything is being runified anyway
        return false;
    }
    var i = lowFreq.indexOf(input.toLowerCase());
    return i >= 0 && i < letterCount;
}

function runifiedSpan(input) {
    var span = document.createElement('span');
    span.classList.add(marker);
    span.innerText = input;
    return span;
}

function translate(input) {
    const normalizedInput = input.normalize();
    let newStr = "";
    let newType = -1;
    let wordStart = true;

    let ret = [];

    function addData(data, type) {
        if(type != newType) {
            if(newStr) {
                ret.push([newType, newStr]);
            }
            newType = type;
            newStr = data;
        } else {
            newStr += data;
        }
        wordStart = !(newStr && newStr[newStr.length - 1].match(/[\wа-яА-Я]/i));
    }

    for (let i = 0; i < normalizedInput.length; i++) {
        var lower = normalizedInput[i].toLowerCase();
        var cyr = (wordStart && cyr2latWordStart[lower]) ? cyr2latWordStart[lower] : cyr2lat[lower];

        if (!transformCyrillic || !cyr) {
            addData(normalizedInput[i], shouldRunify(normalizedInput[i]) ? 1 : 0);
        } else {
            var useTranslit = letterCount == charFreq.length;
            if(!useTranslit) {
                for(let k = 0; k < cyr.length; ++k) {
                    if(shouldRunify(cyr[k])) {
                        useTranslit = true;
                    }
                }
            }
            if(useTranslit) {
                for(let k = 0; k < cyr.length; ++k) {
                    if(letterCount == charFreq.length || shouldRunify(cyr[k])) {
                        addData(cyr[k], 1);
                    } else {
                        var c = lat2cyr[cyr[k]];
                        addData((k != 0 || lower == normalizedInput[i]) ? c : c.toUpperCase(), 0);
                    }
                }
            } else {
                addData(normalizedInput[i], shouldRunify(normalizedInput[i]) ? 1 : 0);
            }
        }
    }
    addData(null, -1);
    return ret;
}

function runifyNode(node, descend=false, parent=true) {
    if(parent) {
        disableStyle();
    }

    var ignore = !node.childNodes;
    if(!ignore && node.classList) {
        for(var k = 0; k < node.classList.length; ++k) {
            if(classBlacklist[node.classList[k]]) {
                ignore = true;
                break;
            }
        }
    }
    if(ignore) {
        if(parent) {
            updateStyle();
        }
        return;
    }

    if(node.tagName) {
        var tag = node.tagName.toLowerCase();

        if(tagBlacklist[tag]) {
            if(parent) {
                updateStyle();
            }
            return;
        }
    }

    var i = 0;
    if(descend && node.children && node.children.length < LIMIT_CHILDREN) {
        for(i = 0; i < node.children.length; ++i) {
            runifyNode(node.children[i], descend, false);
        }
    }

    var fontFamily, additions;

    try {
        fontFamily = window.getComputedStyle(node).getPropertyValue('font-family');
        if(fontFamily.indexOf('Font Awesome') >= 0) {
            additions =
                '!important;font-weight:' + window.getComputedStyle(node).getPropertyValue('font-weight') +
                '!important;text-transform:' + window.getComputedStyle(node).getPropertyValue('text-transform');
        }
    } catch(e) {}

    if(!transformMonospaceFonts && fontFamily && fontFamily.toLowerCase().indexOf('mono') >= 0) {
        return;
    }

    var updated = fontFamily;
    if(fontFamily && !fontFamily.startsWith(FONT)) {
        updated = FONT + ',' + updated;
    }

    if(letterCount == charFreq.length && node.style && updated != fontFamily) {
        setElementFontFamily(node, updated, additions);
    }

    function toNode(e) {
        if(e[0] == 0) {
            return document.createTextNode(e[1]);
        } else {
            var ret = runifiedSpan(e[1]);
            if(updated) {
                setElementFontFamily(ret, updated, additions);
            }
            return ret;
        }
    }

    for(i = 0; i < node.childNodes.length; ++i) {
        if(node.childNodes[i].nodeType == 3) { //text node
            var upd = translate(node.childNodes[i].nodeValue);
            if(upd.length == 0) { //text node ends up being removed. Probably shouldn't even happen?
                node.removeChild(node.childNodes[i]);
                --i;
            } else if(upd.length == 1 && upd[0][0] == 0) {
                if(upd[0][1] != node.childNodes[i].nodeValue) {
                    node.childNodes[i].nodeValue = upd[0][1];
                }
            } else if(upd.length > 1 || (upd.length >= 1 && upd[0][0] == 1)) { //if we add or change nodes
                if(!node.classList.contains(marker)) {
                    var div = document.createElement('div');
                    div.style.display = "inline";
                    for(var j = 0; j < upd.length; ++j) {
                        div.appendChild(toNode(upd[j]));
                    }
                    node.replaceChild(div, node.childNodes[i]);
                } else {
                    if(upd.length == 1) {
                        node.childNodes[i].nodeValue = upd[0][1];
                    } else {
                        var ref = toNode(upd[upd.length - 1]);
                        node.replaceChild(ref, node.childNodes[i]);
                        for(var u = 0; u < upd.length - 1; ++u) {
                            node.insertBefore(toNode(upd[u]), ref);
                        }
                        i += upd.length - 1; //we added a bunch of nodes, update current index to reflect that*/
                    }
                }
            }
        }
    }

    if(node.getAttribute && node.getAttribute(marker) != "true") {
        subscribe(node);
        node.setAttribute(marker, "true");
    }

    subscriber(observer.takeRecords(), node); //remove events related to the edits above from the queue

    if(parent) {
        updateStyle();
    }
}

function subscriber(mutations, ignoreNode=undefined) {
    if(!mutations) {
        return;
    }
    for(var i = 0; i < mutations.length; ++i) {
        if(mutations[i].target == ignoreNode) {
            continue;
        }
        if(mutations[i].type == 'characterData') {
            runifyNode(mutations[i].target);
        } else if(mutations[i].type == 'childList') {
            runifyNode(mutations[i].target, true);
        }
    }
}

function subscribe(node) {
    // Track innerText changes and the like
    if(letterCount < charFreq.length) { //if all chars are runified, all text is already in runes
        observer.observe(node, config1);
    }
    // Tracks textContent changes and new nodes
    observer.observe(node, config2);
}

var config1 = {
    attributes: false,
    attributeOldValue: false,
    characterData: true,
    characterDataOldValue: false,
    childList: false,
    subtree: true
};

var config2 = {
    attributes: false,
    attributeOldValue: false,
    characterData: false,
    characterDataOldValue: false,
    childList: true,
    subtree: false
};

var observer = new MutationObserver(subscriber);

runifyNode(document, true);

GM_addValueChangeListener('letterCount', function(name, old_value, new_value, remote) {
    letterCount = new_value;
    if((old_value == charFreq.length && new_value != charFreq.length) || (old_value != charFreq.length && new_value == charFreq.length)) {
        updateStyle();
    }
    if(old_value > new_value) {
        window.location.reload(false);
    } else {
        runifyNode(document, true);
    }
});

GM_addValueChangeListener('archaic', function(name, old_value, new_value, remote) {
    archaic = new_value;
    allToUpper = archaic;
    allToLower = !archaic;
    updateStyle();
});

GM_registerMenuCommand('Replace one more letter!', function() {
    if(letterCount >= charFreq.length) {
        alert('Already replacing all the known letters!');
    } else {
        alert('Added letter ' + charFreq[letterCount]);
        if(lettersChildren[charFreq[letterCount]]) {
            letterCount += lettersChildren[charFreq[letterCount]];
        }
        GM_setValue('letterCount', ++letterCount);
    }
});

GM_registerMenuCommand('Make one letter turn back (and reload)!', function() {
    if(letterCount <= 0) {
        alert('The script is already doing nothing!');
    } else {
        --letterCount;
        if(letterCount > 1) {
            for(var k in lettersChildren) {
                if(charFreq[letterCount - lettersChildren[k]] == k) {
                    letterCount -= lettersChildren[k];
                    break;
                }
            }
        }
        alert('Removed letter ' + charFreq[letterCount]);
        GM_setValue('letterCount', letterCount);
    }
});

GM_registerMenuCommand('Replace everything with runes', function() {
    GM_setValue('oldCount', letterCount);
    GM_setValue('letterCount', charFreq.length);
});

GM_registerMenuCommand('Make everything normal (and reload)', function() {
    GM_setValue('oldCount', letterCount);
    GM_setValue('letterCount', 0);
});

GM_registerMenuCommand('Undo one of the two options above', function() {
    GM_setValue('letterCount', GM_getValue('oldCount', letterCount));
});

GM_registerMenuCommand('Switch between modern and archaic styles', function() {
    GM_setValue('archaic', !archaic);
    if(archaic) {
        alert('Switching to archaic style');
    } else {
        alert('Switching to modern style (except letters V and X)');
    }
});
