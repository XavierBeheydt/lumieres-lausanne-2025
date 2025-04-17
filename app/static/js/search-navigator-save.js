$(function() {
	function supports_html5_storage() {
		try {
			return 'localStorage' in window && window['localStorage'] !== null;
		} catch (e) {
			return false;
		}
	}
	
	if ( ! supports_html5_storage() ) { return; }
	
	var transResultUrls = [];
	$('ul.results-group-list ul.results-item-list li a[id^="Transcription__"]').each(function () {
		var url = this.href;
		if ( transResultUrls.indexOf(url) === -1 ) {
			transResultUrls.push(url);
		}
	});
	localStorage.setItem('results-trans-list', JSON.stringify(transResultUrls));

	var biblioResultUrls = [];
	$('ul.results-group-list ul.results-item-list li a[id^="Biblio__"]').each(function () {
		var url = this.href;
		if ( biblioResultUrls.indexOf(url) === -1 ) {
			biblioResultUrls.push(url);
		}
	});
	localStorage.setItem('results-biblio-list', JSON.stringify(biblioResultUrls));
	
	$(window).unload(function (){ 
		localStorage.removeItem('results-trans-list'); 
		localStorage.removeItem('results-biblio-list'); 
	});
});