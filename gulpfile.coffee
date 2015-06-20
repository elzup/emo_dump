gulp = require 'gulp'
gutil = require 'gulp-util'
koutSwiss = require 'kouto-swiss'
stylus = require 'gulp-stylus'

$ = require('gulp-load-plugins')()

# config
# src_dir = './src'
# public_dir = './public'

# NOTE: template -> jade, script -> coffee, script -> stylus のがいいかも?
config =
  templates:
    source: './src/jade'
    watch: './src/jade/**/*.jade'
    destination: './emo_dump/templates'
    config:
      pretty: true
  scripts:
    source: './src/coffee'
    watch: './src/coffee/*.coffee'
    destination: './emo_dump/static/javascripts/'
    option:
      bare: true
  stylus:
    source: './src/stylus'
    watch: './src/stylus/*.styl'
    destination: './emo_dump/static/stylesheets/'
  sass:
    source: './src/sass'
    watch: './src/sass/*.sass'
    destination: './emo_dump/static/stylesheets/'

# error handle
handleError = (err) ->
  gutil.log err
  gutil.beep()
  this.emit 'end'

# tasks
gulp.task 'template', ->
#   console.log config.src.jade_files
#   console.log config.src.jade_dir
  gulp
    .src config.templates.watch
    .pipe $.jade(
      config.templates.option
    )
    .on 'error', handleError
    .pipe gulp.dest config.templates.destination

gulp.task 'coffee', ->
  gulp
    .src config.scripts.watch
    .pipe $.coffee()
    .on 'error', handleError
    .pipe gulp.dest config.scripts.destination

gulp.task "stylus", ->
  gulp
    .src config.stylus.watch
    .pipe $.sourcemaps.init()
    .pipe stylus
      compress: true
      use: koutSwiss()
    .pipe $.autoprefixer
      browsers: ['last 2 versions']
    .pipe $.sourcemaps.write('.')
    .on 'error', handleError
    .pipe gulp.dest config.stylus.destination

gulp.task "sass", ->
  gulp
  .src config.sass.watch
  .pipe $.sourcemaps.init()
  .pipe $.sass
    compress: true
  .pipe $.autoprefixer
    browsers: ['last 2 versions']
  .pipe $.sourcemaps.write('.')
  .on 'error', handleError
  .pipe gulp.dest config.sass.destination

# watch
gulp.task 'watch', ->
  gulp.watch config.scripts.watch, ['coffee']
  gulp.watch config.stylus.watch, ['stylus']

#load
gulp.task 'default', ["coffee", "stylus"]
