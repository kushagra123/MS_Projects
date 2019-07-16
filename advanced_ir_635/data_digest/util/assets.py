from flask_assets import Bundle, Environment
import web_interface

bundles = {

    'home_js': Bundle(
        'js/breakpoints.min.js',
        'js/browser.min.js',
        'js/jquery.min.js',
        'js/jquery.min.js',
        'js/jquery.scrollex.min.js',
        'js/jquery.scrolly.min.js',
        'js/main.js',
        'js/util.js',
        output='gen/main.js'),

    'home_css': Bundle(
        'css/font-awesome.min.css',
        'css/main.css',
        output='gen/main.css'),
}
Bundle(depends='sass/main.scss')

assets = Environment(main)

assets.register(bundles)
