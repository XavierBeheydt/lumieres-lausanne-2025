# settings_ckeditor_configs.py

from django.conf import settings

# -----------------
# CKEDITOR Configs
# -----------------

CKEDITOR_CTRL = 0x110000
CKEDITOR_SHIFT = 0x220000

CKEDITOR_CONFIGS = {
    'project_ckeditor': {
        'skin': 'v2',
        'contentsCss': f"{settings.STATIC_URL}css/project_description.css",
        'bodyClass': 'project-description-content',
        'bodyId': 'project-description-content-id',
        'width': 750,
        'height': 300,
        'extraPlugins': 'footnote',
        'autoGrow_minHeight': '200',
        'autoGrow_maxHeight': '800',
        'autoGrow_bottomSpace': '50',
        'removePlugins': 'flash,iframe,bidi',
        'stylesSet': [
            {
                'name': 'Normal',
                'element': 'p',
                'attributes': {'class': 'normal'}
            },
            {
                'name': 'Section',
                'element': 'p',
                'attributes': {'class': 'section'}
            }
        ],
        'format_tags': 'p;h2;h3',
        'toolbar': 'Project',
        'toolbar_Project': (
            ['Cut', 'Copy', 'Paste', 'PasteText', '-', 'SelectAll', '-', 'Source'],
            ['Image', 'Smiley', 'SpecialChar', 'PageBreak', 'Footnote'],
            ['Link', 'Unlink', 'Anchor'],
            ['Maximize', '-', 'About'],
            '/',
            ['Styles', 'Format'],
            ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', 'Blockquote'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
        ),
    },

    'transcription_ckeditor': {
        'skin': 'v2',
        'contentsCss': f"{settings.STATIC_URL}css/tinyMCE_transcripts.css",
        'bodyClass': 'cked-content',
        'width': 880,
        'height': 500,
        'extraPlugins': 'overline,transcription,correction,notes,illeg,footnote',
        'language': 'fr',
        'removePlugins': 'flash,iframe,bidi,scayt',
        'removeFormatTags': 'font',
        'stylesSet': [
            {
                'name': 'Versification',
                'element': 'p',
                'attributes': {'class': 'verse'}
            }
        ],
        'format_tags': 'p;h1;h2;h3',
        'toolbar': 'Transcription',
        'toolbar_Transcription': (
            ['Save', '-'],
            ['SelectAll', 'Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo', '-', 'Find', 'Replace', '-', 'ShowBlocks', 'Source', '-', 'Maximize'],
            '/',
            ['Italic', 'Underline', 'Overline', 'Superscript'],
            ['Image', 'Table', 'SpecialChar', '-', 'Link', 'Unlink'],
            ['Styles', 'Format', 'BGColor'],
            '/',
            ['Added', 'Suppressed', 'Notes', 'Footnote'],
            ['Supplied', 'Unclear', 'Illeg', 'Correction']
        ),
        'keystrokes': [
            [CKEDITOR_CTRL + CKEDITOR_SHIFT + 85, 'superscript'],  # ctrl+shift+u
            [CKEDITOR_CTRL + CKEDITOR_SHIFT + 65, 'correctionDialog'],  # ctrl+shift+a
            [CKEDITOR_CTRL + 90, 'undo'],  # ctrl+z
            [CKEDITOR_CTRL + 89, 'redo'],  # ctrl+y
            [CKEDITOR_CTRL + 76, 'link'],  # ctrl+l
            [CKEDITOR_CTRL + 66, 'bold'],  # ctrl+b
            [CKEDITOR_CTRL + 73, 'italic'],  # ctrl+i
            [CKEDITOR_CTRL + 85, 'underline']  # ctrl+u
        ],
        'specialChars': (
            ('&szlig;', 'Latin small letter sharp s'),
            ['%', 'Percent Sign'],
            (u'\u2021', 'Double Dagger'),
            (u'\u2020', 'Dagger'),
            (u'\u222B', 'Integral'),
            ('&pound;', 'Pound Sign'),
            ('&sect;', 'Section sign'),
            ('&para;', 'Paragraph Sign'),
            ('&frac14;', 'Vulgar fraction one quarter'),
            ('&frac12;', 'Vulgar fraction one half'),
            ('&frac34;', 'Vulgar fraction three quarters'),
            ('[', '['),
            (']', ']'),
            ('&alpha;', 'alpha'),
            ('&beta;', 'beta'),
            ('&gamma;', 'gamma'),
            ('&delta;', 'delta'),
            ('&epsilon;', 'epsilon'),
            ('&zeta;', 'zeta'),
            ('&eta;', 'eta'),
            ('&theta;', 'theta'),
            ('&iota;', 'iota'),
            ('&kappa;', 'kappa'),
            ('&lambda;', 'lambda'),
            ('&mu;', 'mu'),
            ('&nu;', 'nu'),
            ('&xi;', 'xi'),
            ('&omicron;', 'omicron'),
            ('&pi;', 'pi'),
            ('&rho;', 'rho'),
            ('&sigmaf;', 'sigmaf'),
            ('&sigma;', 'sigma'),
            ('&tau;', 'tau'),
            ('&upsilon;', 'upsilon'),
            ('&phi;', 'phi'),
            ('&chi;', 'chi'),
            ('&psi;', 'psi'),
            ('&omega;', 'omega'),
            ('ά', 'ά'),
            ('ἀ', 'ἀ'),
            ('ἅ', 'ἅ'),
            ('ᾴ', 'ᾴ'),
            ('Ἄ', 'Ἄ'),
            ('ὅ', 'ὅ'),
            (' ̔', ' ̔'),
            ('ὀ', 'ὀ'),
            ('ό', 'ό'),
            ('Ὀ', 'Ὀ'),
            ('έ', 'έ'),
            ('ἐ', 'ἐ'),
            ('ἔ', 'ἔ'),
            ('ῶ', 'ῶ'),
            ('ώ', 'ώ'),
            ('ὠ', 'ὠ'),
            ('ῴ', 'ῴ'),
            ('ξ', 'ξ'),
            ('ζ', 'ζ'),
            ('ί', 'ί'),
            ('ἰ', 'ἰ'),
            ('ῖ', 'ῖ'),
            ('ἴ', 'ἴ'),
            ('ἶ', 'ἶ'),
            ('Ἶ', 'Ἶ'),
            ('ή', 'ή'),
            ('ῆ', 'ῆ'),
            ('ἥ', 'ἥ'),
            ('ἡ', 'ἡ'),
            ('ῥ', 'ῥ'),
            ('ῦ', 'ῦ'),
            ('ὑ', 'ὑ'),
            ('ὐ', 'ὐ'),
            ('ύ', 'ύ'),
            ('ὕ', 'ὕ'),
            ('ὗ', 'ὗ')
        ),
    },
    
    'note_ckeditor': {
        'skin': 'v2',
        'contentsCss': f"{settings.STATIC_URL}css/main2.css",
        'bodyClass': 'note-content',
        'width': 650,
        'height': 120,
        'resize_minWidth': 650,
        'resize_maxWidth': 650,
        'extraPlugins': 'autogrow,transcription',
        'autoGrow_minHeight': '120',
        'autoGrow_maxHeight': '400',
        'removePlugins': 'flash,iframe',
        'shiftEnterMode': '2',
        'format_tags': 'p;h1;h2;h3',
        'toolbar': 'Basic',
        'toolbar_Basic': (
            ['Bold', 'Italic', 'Underline', '-', 'Subscript', 'Superscript'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock', '-', 'NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Cut', 'Copy', 'Paste', 'PasteText'],
            ['Undo', 'Redo', '-', 'About'],
        ),
    },
}

# Add 'envelope_ckeditor' by copying 'transcription_ckeditor'
CKEDITOR_CONFIGS['envelope_ckeditor'] = CKEDITOR_CONFIGS['transcription_ckeditor'].copy()
CKEDITOR_CONFIGS['envelope_ckeditor']['height'] = 120
