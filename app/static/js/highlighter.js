/*****
 * 
 *    Copyright (C) 2010-2012 Université de Lausanne, RISET
 *    < http://www.unil.ch/riset/ >
 *
 *    This file is part of Lumières.Lausanne.
 *    Lumières.Lausanne is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    Lumières.Lausanne is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *    This copyright notice MUST APPEAR in all copies of the file.                      
 *
 ****/
$(function() {
	var   hl 	= unescape(window.location.search.replace(/^(?:.*[&\?]q(?:\=([^&]*))?)?.*$/i,
														  "$1"))
		, map 	= {
			// escape reserved symbols in regular expressions
			'[': "\\[",	']': "\\]", '{': "\\{", '}': "\\}", '(': "\\(",   ')': "\\)",
			'.': "\\.", '?': "\\?", '+': "\\+", '*': "\\*", '\\': "\\\\", '|': "\\|",
			'^': "\\^",	'$': "\\$",
			
			// Those mappings reflect what is done by solr as defined by the 
			// mapping-ISOLatin1Accent.txt configuration file.
			
			// mapping for A
			"A":		"[A\u00C0-\u00C6]",
			"\u00C0": 	"[A\u00C0-\u00C6]",
			"\u00C1": 	"[A\u00C0-\u00C6]",
			"\u00C2": 	"[A\u00C0-\u00C6]",
			"\u00C3": 	"[A\u00C0-\u00C6]",
			"\u00C4": 	"[A\u00C0-\u00C6]",
			"\u00C5": 	"[A\u00C0-\u00C6]",
			"\u00C6":	"AE",
			// mapping for C
			"C":		"[C\u00C7]",
			"\u00C7":	"[C\u00C7]",
			// mapping for D
			"D":		"[D\u00D0]",
			"\u00D0":	"[D\u00D0]",
			// mapping for E
			"E":		"[E\u00C8-\u00CB\u00C6\u0152]",
			"\u00C8":	"[E\u00C8-\u00CB\u00C6\u0152]",
			"\u00C9":	"[E\u00C8-\u00CB\u00C6\u0152]",
			"\u00CA":	"[E\u00C8-\u00CB\u00C6\u0152]",
			"\u00CB":	"[E\u00C8-\u00CB\u00C6\u0152]",
			// mapping for I
			"I": 		"[I\u00CC-\u00CF\u0132]",
			"\u00CC": 	"[I\u00CC-\u00CF\u0132]",
			"\u00CD": 	"[I\u00CC-\u00CF\u0132]",
			"\u00CE": 	"[I\u00CC-\u00CF\u0132]",
			"\u00CF": 	"[I\u00CC-\u00CF\u0132]",
			"\u0132":	"IJ",
			// mapping for J
			"J": 		"[J\u0132]",
			// mapping for N
			"N":		"[N\u00D1]",
			"\u00D1":	"[N\u00D1]",
			// mapping for O
			"O": 		"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D2":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D3":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D4":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D5":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D6":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u00D8":	"[o\u00D2-\u00D6\u00D8\u0152]",
			"\u0152":	"OE",
			// mapping for T
			"T":		"[T\u00DE]",
			"H":		"[H\u00DE]",
			"\u00DE":	"TH",
			// mapping for U
			"U": 		"[U\u00D9-\u00DC]",
			"\u00D9":	"[U\u00D9-\u00DC]",
			"\u00DA":	"[U\u00D9-\u00DC]",
			"\u00DB":	"[U\u00D9-\u00DC]",
			"\u00DC":	"[U\u00D9-\u00DC]",
			// mapping for Y
			"Y": 		"[Y\u00DD\u0178]",
			"\u00DD":	"[Y\u00DD\u0178]",
			"\u0178":	"[Y\u00DD\u0178]",
			
			// mapping for a
			"a":		"[a\u00E0-\u00E6]",
			"\u00E0": 	"[a\u00E0-\u00E6]",
			"\u00E1": 	"[a\u00E0-\u00E6]",
			"\u00E2": 	"[a\u00E0-\u00E6]",
			"\u00E3": 	"[a\u00E0-\u00E6]",
			"\u00E4": 	"[a\u00E0-\u00E6]",
			"\u00E5": 	"[a\u00E0-\u00E6]",
			"\u00E6":	"ae",
			// mapping for c
			"c":		"[c\u00E7]",
			"\u00E7":	"[c\u00E7]",
			// mapping for d
			"d":		"[d\u00F0]",
			"\u00F0":	"[d\u00F0]",
			// mapping for e
			"e":		"[e\u00E8-\u00EB\u00E6\u0153]",
			"\u00E8":	"[e\u00E8-\u00EB\u00E6\u0153]",
			"\u00E9":	"[e\u00E8-\u00EB\u00E6\u0153]",
			"\u00EA":	"[e\u00E8-\u00EB\u00E6\u0153]",
			"\u00EB":	"[e\u00E8-\u00EB\u00E6\u0153]",
			// mapping for i
			"i": 		"[i\u00EC-\u00EF\u0133]",
			"\u00EC": 	"[i\u00EC-\u00EF\u0133]",
			"\u00ED": 	"[i\u00EC-\u00EF\u0133]",
			"\u00EE": 	"[i\u00EC-\u00EF\u0133]",
			"\u00EF": 	"[i\u00EC-\u00EF\u0133]",
			"\u0133":	"ij",
			// mapping for j
			"j": 		"[j\u0133]",
			// mapping for n
			"n":		"[n\u00F1]",
			"\u00F1":	"[n\u00F1]",
			// mapping for o
			"o": 		"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F2":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F3":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F4":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F5":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F6":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u00F8":	"[o\u00F2-\u00F6\u00F8\u0153]",
			"\u0153":	"oe",
			// mapping for s
			"s":		"[s\u00DF]",
			"\u00DF":	"ss",
			// mapping for t
			"t":		"[t\u00FE]",
			"h":		"[h\u00FE]",
			"\u00FE":	"th",
			// mapping for u
			"u": 		"[u\u00F9-\u00FC]",
			"\u00F9":	"[u\u00F9-\u00FC]",
			"\u00FA":	"[u\u00F9-\u00FC]",
			"\u00FB":	"[u\u00F9-\u00FC]",
			"\u00FC":	"[u\u00F9-\u00FC]",
			// mapping for y
			"y": 		"[y\u00FD\u00FF]",
			"\u00FD":	"[y\u00FD\u00FF]",
			"\u00FF":	"[y\u00FD\u00FF]",
		}
		, reStr = ""
		, re
		, i
		, c;
	if ( hl == null || hl.length === 0 ) { return; }
	for ( i = 0; i < hl.length; i++ ) {
		c = hl[i];
		if ( c in map ) {
			reStr += map[c];
		} else {
			reStr += hl[i];
		}
	}
	re = new RegExp("(" + reStr.replace(/\s+/, "|") + ")", "i");
	function walker(node) {
		var   match
			, range
			, wrapper
			, i = 0;
		switch ( node.nodeType ) {
			
		case 3: // text node, highlight the search query
			match = node.nodeValue.match(re);
			if ( match ) {
				range = document.createRange();
				wrapper = document.createElement("span");
				wrapper.setAttribute("style", "background:yellow");
				range.setStart(node, match.index);
				range.setEnd(node, match.index + match[0].length);
				range.surroundContents(wrapper);
				return 1; // to skip the newly created node
			};
			break;
		case 1: // element node, do the recursion
			for ( i = 0; i < node.childNodes.length; i++ ) {
				i += walker(node.childNodes[i]);
			}
			break;

		default: // stop the recursion for every other type
			break;
		
		}
		return 0;
	}
	$(".field_value, .transcription-data").each(function () { walker(this); });
});