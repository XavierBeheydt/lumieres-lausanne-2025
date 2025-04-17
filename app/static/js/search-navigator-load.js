$(function() {
	function supports_html5_storage() {
		try {
			return 'localStorage' in window && window['localStorage'] !== null;
		} catch (e) {
			return false;
		}
	}
	
	if ( ! supports_html5_storage() ) { return; }
	
	var transResultUrlsStr = localStorage.getItem('results-trans-list');
	var biblioResultUrlsStr = localStorage.getItem('results-biblio-list');
	
	if ( ! biblioResultUrlsStr || ! transResultUrlsStr ) { return; }
	
	var resultUrls = JSON.parse(biblioResultUrlsStr)
		, currentItemIndex = -1
		, navigator = '<div class="search-navigator">'
		, pathFinder = function (path, index) {
			if ( path !== null && path.indexOf(window.location.pathname) !== -1 ) {
				currentItemIndex = index;
				return true;
			}
			return false;
		};
	
	// if we didn't fin the current url in the biblio list, check in the trans list
	if ( ! resultUrls.some(pathFinder) ) {
		resultUrls = JSON.parse(transResultUrlsStr);
		if ( ! resultUrls.some(pathFinder) ) {
			return;
		}
	}
	
	if ( currentItemIndex > 0 ) { 
		navigator += '<a href="' + resultUrls[currentItemIndex - 1] + '">&laquo; Fiche précédente</a>';
	} else {
		navigator += '<span>&laquo; Fiche précédente</span>';
	}
	if ( currentItemIndex < resultUrls.length - 1 ) { 
		navigator += '<a href="' + resultUrls[currentItemIndex + 1] + '">Fiche suivante &raquo;</a>';
	} else {
		navigator += '<span>Fiche suivante &raquo;</span>';
	}

	$('div.content').prepend(navigator);
});