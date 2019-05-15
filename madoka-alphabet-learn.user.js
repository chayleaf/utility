// ==UserScript==
// @name         Madoka ftw
// @namespace    *
// @version      0.1.3.3
// @description  Madoka ftw
// @author       pavlukivan
// @match        *://*/*
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_addValueChangeListener
// @grant        GM_registerMenuCommand
// @grant        GM_getResourceURL
// @resource     madokaFont https://github.com/pavlukivan/utility/raw/master/MadokaRunes-2.0.ttf
// ==/UserScript==

//config start
var archaic = GM_getValue('archaic', false);
var letterCount = GM_getValue('letterCount', 0); //letters to replace, ordered by usage frequency
var allToUpper = !archaic;
var allToLower = archaic;
var transformCyrillic = true;

//config that you probably shouldn't change
var LIMIT_CHILDREN = 1000; //don't descend into elements if they have more than 1000 children
var finalTransforms = {'v':'V', 'x':'X'}; //v and x letters' modern style is unknown, use archaic instead
var styleContent = "font-family:MadokaRunes!important;";
var tagBlacklist = ["text","code"]; //script, style and title are there by default
var lettersChildren = {'A':1, 'O':1, 'U':1}; //count of letters that should be activated along with these. Currently only zero/one is supported.
//config end

//       charset: 1234567890qwertyuiopasdfghjklzxcvbnmßüöä. English wikipedia is used for reference. Upper because 'ß'.toUpperCase() == 'SS', not 'ẞ'
//var charFreq = 'EAIOTNRSLDCUHMGPFYB0VW1K23549ZX687JQÜÄÖẞ';
var charFreq = 'EAÄIOÖTNRSLDCUÜHMGPFYB0VW1K23549ZX687JQẞ'; //changed order of umlauted chars

var lowFreq = charFreq.toLowerCase();

var marker = "w17ch_k155"; //a random string used to mark stuff already affected by script

letterCount = Math.min(charFreq.length, letterCount);
GM_addStyle("@font-face { font-family:MadokaRunes;src:url('" + GM_getResourceURL('madokaFont') + "'); }");
var style = GM_addStyle((letterCount == charFreq.length ? "*" : "." + marker) + " { " + styleContent + " }");

//https://github.com/greybax/cyrillic-to-translit-js/blob/master/CyrillicToTranslit.js
const cyr2lat = {"а": "a","б": "b","в": "v","ґ": "g","г": "g","д": "d","е": "e","ё": "yo","є": "ye","ж": "j","з": "z","и": "i","і": "i","ї": "yi","й": "y","к": "k","л": "l","м": "m","н": "n","о": "o","п": "p","р": "r","с": "s","т": "t","у": "u","ф": "f","х": "h","ц": "c","ч": "ch","ш": "sh","щ": "sh'","ъ": "'","ы": "y","ь": "'","э": "e","ю": "yu","я": "ya",};
const cyr2latWordStart = {"е":"ye",};
//used for translating characters that arent available yet back to cyrillics (e.g. if y in ye isnt available, we show y as й and e as runes)
var lat2cyr = {"a":"а","b":"б","c":"ц","d":"д","e":"е","f":"ф","g":"г","h":"х","i":"и","j":"ж","k":"к","l":"л","m":"м","n":"н","o":"о","p":"п","q":"к","r":"р","s":"с","t":"т","u":"у","v":"в","w":"в","x":"з","y":"й","z":"з",};
finalTransforms['SS'] = 'ẞ';

function shouldRunify(input) {
	var i = lowFreq.indexOf(input.toLowerCase());
	return i >= 0 && i < letterCount;
}

function runifiedSpan(input) {
	var text = "";
	for(var j = 0; j < input.length; ++j) {
		var i = lowFreq.indexOf(input[j].toLowerCase());
		if(i < 0) {
			text += input[j];
		} else {
			var c = ((!allToUpper && (input[j] === input.toLowerCase() || allToLower)) ? lowFreq[i] : charFreq[i]);
			if(finalTransforms[c]) {
				text += finalTransforms[c];
			} else {
				text += c;
			}
		}
	}

	var span = document.createElement('span');
	span.classList.add(marker);
	span.innerText = text;
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
			var useTranslit = false;
			for(let k = 0; k < cyr.length; ++k) {
				if(shouldRunify(cyr[k])) {
					useTranslit = true;
				}
			}
			if(useTranslit) {
				for(let k = 0; k < cyr.length; ++k) {
					if(shouldRunify(cyr[k])) {
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

function runifyNode(node, descend=false) {
	if((node.classList && node.classList.contains(marker)) || !node.childNodes) { //don't change stuff that IS the changes
		return;
	}

	if(node.tagName) {
		var tag = node.tagName.toLowerCase();

		if(tag == "script" || tag == "style" || tag == "title" || tag == "textarea" || tagBlacklist.indexOf(tag) >= 0) {
			return;
		}
	}

	var i = 0;
	if(descend && node.children && node.children.length < LIMIT_CHILDREN) {
		for(i = 0; i < node.children.length; ++i) {
			runifyNode(node.children[i], descend);
		}
	}

	if(node.getAttribute && node.getAttribute(marker) != "true") {
		subscribe(node);
		node.setAttribute(marker, "true");
	}

	function toNode(e) {
		if(e[0] == 0) {
			return document.createTextNode(e[1]);
		} else {
			return runifiedSpan(e[1]);
		}
	}

	for(i = 0; i < node.childNodes.length; ++i) {
		if(node.childNodes[i].nodeType == 3) { //text node
			var upd = translate(node.childNodes[i].nodeValue);
			if(upd.length == 0) { //text node ends up being removed
				node.removeChild(node.childNodes[i]);
				--i;
			} else if(upd.length > 1 || (upd.length >= 1 && upd[0][0] == 1)) { //if we add or change nodes
				var ref = toNode(upd[upd.length - 1]);
				node.replaceChild(ref, node.childNodes[i]);
				for(var j = 0; j < upd.length - 1; ++j) {
					node.insertBefore(toNode(upd[j]), ref);
				}
				i += upd.length - 1; //we added a bunch of nodes, update current index to reflect that
			}
		}
	}
}

function updateStyle(node, descend=false) {
	var i = 0;
	if(descend && node.children) {
		for(i = 0; i < node.children.length; ++i) {
			updateStyle(node.children[i], descend);
		}
	}

	if(!node.childNodes) {
		return;
	}

	for(i = 0; i < node.childNodes.length; ++i) {
		if(node.childNodes[i].nodeType == 1 && node.childNodes[i].classList && node.childNodes[i].classList.contains(marker)) {
			var text = "";
			var input = node.childNodes[i].innerText;
			for(var j = 0; j < input.length; ++j) {
				var k = lowFreq.indexOf(input[j]);
				if(k < 0) {
					k = charFreq.indexOf(input[j]);
				}

				if(k < 0) {
					text += input[j];
				} else {
					var c = ((!allToUpper && (input[j] === input.toLowerCase() || allToLower)) ? lowFreq[k] : charFreq[k]);
					if(finalTransforms[c]) {
						text += finalTransforms[c];
					} else {
						text += c;
					}
				}
			}
			node.childNodes[i].innerText = text;
		}
	}
}


function subscriber(mutations) {
	if(!mutations) {
		return;
	}
	for(var i = 0; i < mutations.length; ++i) {
		if(mutations[i].type == 'characterData') {
			runifyNode(mutations[i].target);
		} else if(mutations[i].type == 'childList') {
			runifyNode(mutations[i].target, true);
		}
	}
}

function subscribe(node) {
	// Track innerText changes and the like
	observer.observe(node, config1);
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
	if(old_value == charFreq.length && new_value != charFreq.length) {
		style.innerHTML = "." + marker + " { " + styleContent + " }";
	} else if(old_value != charFreq.length && new_value == charFreq.length) {
		style.innerHTML = "* { " + styleContent + " }";
	}
	runifyNode(document, true);
});

GM_registerMenuCommand('Replace one more letter!', function() {
	if(letterCount >= charFreq.length) {
		alert('Already replacing all the known letters!');
	} else {
		if(lettersChildren[charFreq[letterCount]]) {
			letterCount += lettersChildren[charFreq[letterCount]];
		}
		++letterCount;
		GM_setValue('letterCount', letterCount);
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
		GM_setValue('letterCount', letterCount);
		window.location.reload(false);
	}
});

GM_registerMenuCommand('Replace everything with runes', function() {
	GM_setValue('oldCount', letterCount);
	letterCount = charFreq.length;
	GM_setValue('letterCount', letterCount);
});

GM_registerMenuCommand('Make everything normal (and reload)', function() {
	GM_setValue('oldCount', letterCount);
	letterCount = 0;
	GM_setValue('letterCount', letterCount);
	window.location.reload(false);
});

GM_registerMenuCommand('Undo one of the two above options', function() {
	var oldLC = letterCount;
	letterCount = GM_getValue('oldCount', letterCount);;
	GM_setValue('letterCount', letterCount);
	if(letterCount < oldLC) {
		window.location.reload(false);
	}
});

GM_registerMenuCommand('Switch between modern and archaic styles', function() {
	archaic = !archaic;
	allToUpper = !archaic;
	allToLower = archaic;
	GM_setValue('archaic', archaic);
	updateStyle(document, true);
	if(archaic) {
		alert('Switching to archaic style');
	} else {
		alert('Switching to modern style (except letters V and X)');
	}
});