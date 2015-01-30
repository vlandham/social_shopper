var _ = require('underscore');
var argv = require('minimist')(process.argv.slice(2));
_.mixin( require('underscore.deferred') );
var inflection = require('inflection');
var Twit = require('twit');
var T = new Twit(require('./config.js'));
var handlebars = require("handlebars");
var wordfilter = require('wordfilter');
var fs = require('fs');
var pos = require('pos');

var markov = require('markov');



Array.prototype.pick = function() {
  return this[Math.floor(Math.random()*this.length)];
};

Array.prototype.pickRemove = function() {
  var index = Math.floor(Math.random()*this.length);
  return this.splice(index,1)[0];
};

function getConsumer() {
  var consumers = [
    {'handle': "@Nordstrom",
          'data': "data/nordstrom.jsonlines"},
    {'handle': "@Macys",
          'data': "data/macys.jsonlines"},
    {'handle': "@Sephora",
          'data': "data/sephora.jsonlines"}
  ];

  return consumers[1];

}

function getProduct(consumer) {
  var dfd = new _.Deferred();
  var filename = consumer.data;
  var products = [];
  fs.readFile(filename, 'utf8', function(error, data) {
    var lines = data.split("\n");
    lines.forEach(function(line) {
      try {
        var product = JSON.parse(line);
        products.push(product);
      } catch (ex) {
        // console.log("error parsing: " + line);
      }

    });
    dfd.resolve(_.sample(products));
  });

  return dfd.promise();
}

function generateSentence(product, consumer) {
  var dfd = new _.Deferred();
  var filename = "data/text.json"
  fs.readFile(filename, 'utf8', function(error, data) {
    var json = JSON.parse(data);
    var sections = ["intro", "query"];
    var sentence = "";
    sections.forEach(function(section) {
      sentence = sentence + " " + _.sample(json[section])
    });

    var template = handlebars.compile(sentence);
    var data = {'product':product,
                'consumer': consumer};

    console.log(data);
    var result = template(data);
    dfd.resolve(result);
   
    // sentences = _.filter(sentences, function(el) {
    //   var words = new pos.Lexer().lex(el);
    //   var taggedWords = new pos.Tagger().tag(words);
    //   taggedWords = _.map(taggedWords, function(el) {
    //     return el[1];
    //   });
    //   var NNP = !_.isNull(_.flatten(taggedWords).join(' ').match(/NN/));
    //   var NN_VB = !_.isNull(_.flatten(taggedWords).join(' ').match(/(NN.?|PRP) VB[ZP]/));
    //   //if (NNP & NN_VB) 
    //   //console.log(el, taggedWords.join(' '))
    //   return NNP & NN_VB;
    // });
    // sentences = _.map(sentences, function(el) {
    //   return el.replace(/ +/g, ' ').replace(/\\[.*\\]/g,'').trim();
    // });
    // console.log(sentences.length);
    // //console.log(sentences);
    // dfd.resolve('Startup idea: ' + _.sample(sentences, 1));
   
  });
  return dfd.promise();
}

function generateFiller() {
  var dfd = new _.Deferred();
  var m = markov(2);

  var filename = "data/filler.txt"
  fs.readFile(filename, 'utf8', function(error, data) {
    m.seed(data, function() {
      var word = m.pick();
      console.log(word);
      var sentence = m.fill(word, 15);
      var total = 0;
      sentence = sentence.filter(function(w) {
        total += w.length;
        return total < 140;
      });
      punct = [".","!","?"]
      sentence = sentence.join(" ").split(/[.\?\!]/)[0] + _.sample(punct)

      if(sentence.length < 60) {
        pins = JSON.parse(fs.readFileSync('./data/pintrest_links.js', 'utf8'));
        sentence = sentence + " " + _.sample(pins);
      } 
      dfd.resolve(sentence);

    });

  });
  return dfd.promise();
}


function tweet() {
  var consumer = getConsumer();

  getProduct(consumer).then(function(product) {
    if(argv.f) {
      return generateFiller(product);
    } else {
      return generateSentence(product, consumer);
    }
  }).then(function(myTweet) {

    console.log(myTweet);
    if(!argv.t && !argv.test) {
      T.post('statuses/update', { status: myTweet }, function(err, reply) {
        if (err) {
          console.log('error:', err);
        }
        else {
          console.log('reply:', reply);
        }
      });
    }
  });
}

tweet();
