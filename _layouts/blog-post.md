<!DOCTYPE html>
<html lang="en">

<head>
    <title>{{page.title}}</title>
    <meta name="description"
        content="{{ page.discription }}">
    <meta name="keywords"
        content="{{ page.keywords }}">
    <meta name="author" content="Whatsapp Group Link">
    <meta charset="UTF-8">
<link rel="icon" type="image/x-icon" href="{{ site.url }}/images/logo.png">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YH3VZ65152"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-YH3VZ65152');
</script>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="{{ "/assets/css/main.css" | relative_url }}">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Lato">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Montserrat">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">



    <style>
    .w3-round2{
      border-radius:10px;
    }
    img {
      border-radius:15px;
    }
    .br10 {
        border-radius :15px;
        padding:6px 18px;
        margin:3px;
    }
    a{
        text-decoration:none;
    }
        body,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            font-family: "Lato", sans-serif
        }

        .w3-bar,
        h1,
        button {
            font-family: "Montserrat", sans-serif
        }

        .w3-content {
            max-width: 1100px;
        }

        .w3-rnd {
            border-radius: 30px;
        }
    </style>
</head>

<body>

    {% include header-top.md %}
{% include nav.md %}
 
    <!-- Header -->
    <div class="w3-padding w3-content">
       <a href="{{ site.url }}"><b>Home</b></a> / <a href="{{ site.url }}/{{ page.permalink }}">{{ page.title}}</a>
    </div>
   <div class="w3-row w3-content">
  <div class="w3-twothird">
    <div class="w3-content w3-padding">
       {{ page.content }}
    </div>
    </div>

  <div class="w3-third space w3-padding">

  <div class="w3-row" style="margin-top: 8px;">
  <h2 class="w3-xlarge w3-margin-top">Related Links</h2>
</div>

  <div class="w3-row w3-margin-top w3-light-grey" style="padding:12px; border-radius: 15px;">
  <h3 class="w3-large">Whatsapp Group Links :</h3>
  <hr style="border:1px solid #ffffff; margin:8px 0px;">
 {% for post in site.categories.Group-Links %}
    {% if post.url %}
        <a class="w3-tag w3-white br10" href="{{ post.url }}">{{ post.title }}</a></li>
    <hr style="border:0px #ffffff; margin:8px 0px;">
    {% endif %}
  {% endfor %}

  </div>

<div class="w3-row w3-margin-top w3-light-grey" style="padding:12px; border-radius: 15px;">
  <h3 class="w3-large">Posts :</h3>
  <hr style="border:1px solid #ffffff; margin:8px 0px;">
 {% for post in site.categories.Posts %}
    {% if post.url %}
        <a class="w3-tag w3-white br10" href="{{ post.url }}">{{ post.title }}</a></li>
    <hr style="border:0px #ffffff; margin:8px 0px;">
    {% endif %}
  {% endfor %}

  </div>



  <div class="w3-row w3-margin-top w3-border w3-display-container" style="padding:12px; border-radius: 15px; height:300px;">
 <div class="w3-display-middle"> Ads Here</div>

  </div>

</div>
</div>
</div>

   {% include footer.md %}

   <script>
function myFunction2(id) {
  var x = document.getElementById(id);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
  } else { 
    x.className = x.className.replace(" w3-show", "");
  }
}
</script>


</body>

</html>
