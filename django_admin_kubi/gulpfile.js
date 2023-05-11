"use strict";

var gulp = require('gulp'),
  sass = require('gulp-sass')(require('sass')),
  del = require('del'),
  uglify = require('gulp-uglify'),
  cleanCSS = require('gulp-clean-css'),
  rename = require("gulp-rename"),
  merge = require('merge-stream'),
  autoprefixer = require('gulp-autoprefixer');

// Clean task
gulp.task('clean', function () {
  return del(['dist', 'assets/css/app.css']);
});

// Copy third party libraries from node_modules into /vendor
gulp.task('vendor:js', function () {
  return gulp.src([
    './node_modules/bootstrap/dist/js/*',
    './node_modules/@popperjs/core/dist/umd/popper.*'
  ])
    .pipe(gulp.dest('./assets/js/vendor'));
});

// Copy bootstrap-icons from node_modules into /fonts
gulp.task('vendor:fonts', function () {
  return gulp.src([
    './node_modules/bootstrap-icons/**/*',
    '!./node_modules/bootstrap-icons/package.json',
    '!./node_modules/bootstrap-icons/README.md',
  ])
    .pipe(gulp.dest('./assets/fonts/bootstrap-icons'))
});

// vendor task
gulp.task('vendor', gulp.parallel('vendor:fonts', 'vendor:js'));

// Copy vendor's js to /dist
gulp.task('vendor:build', function () {
  var jsStream = gulp.src([
    './assets/js/vendor/bootstrap.bundle.min.js',
    './assets/js/vendor/popper.min.js'
  ])
    .pipe(gulp.dest('./static/admin/js/vendor'));
  var fontStream = gulp.src(['./assets/fonts/bootstrap-icons/**/*.*']).pipe(gulp.dest('./static/admin/fonts/bootstrap-icons'));
  return merge(jsStream, fontStream);
})

// Compile SCSS(SASS) files
gulp.task('scss', function compileScss() {
  return gulp.src(['./assets/sass/app.scss'])
    .pipe(sass.sync({
      outputStyle: 'expanded'
    }).on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(gulp.dest('./assets/css'))
});

// Minify CSS
gulp.task('css:minify', gulp.series('scss', function cssMinify() {
  return gulp.src("./assets/css/*.css")
    .pipe(cleanCSS())
    .pipe(rename({
      suffix: '.min'
    }))
    .pipe(gulp.dest('./static/admin/css'));
}));

// Minify Js
gulp.task('js:minify', function () {
  return gulp.src([
    './assets/js/app.js'
  ])
    .pipe(uglify())
    .pipe(rename({
      suffix: '.min'
    }))
    .pipe(gulp.dest('./static/admin/js'));
});

// Configure the browserSync task and watch file path for change
gulp.task('watch', function browserDev(done) {
  gulp.watch(['assets/sass/*.scss', '!assets/scss/bootstrap/**'], gulp.series('css:minify', function cssBrowserReload(done) {
    done(); //Async callback for completion.
  }));
  gulp.watch('assets/js/app.js', gulp.series('js:minify', function jsBrowserReload(done) {
    done();
  }));
  done();
});

// Build task
gulp.task("build", gulp.series(gulp.parallel('css:minify', 'js:minify', 'vendor'), 'vendor:build', function copyAssets() {
  return gulp.src([
    "assets/img/**"
  ], { base: './' })
    .pipe(gulp.dest('dist'));
}));

// Default task
gulp.task("default", gulp.series("clean", 'build'));