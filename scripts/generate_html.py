#!/usr/bin/env python3

HTML = """
<style>
p {
  font-size: 1.2rem;
  text-align: center;
}
a {
  outline: none;
  text-decoration: none;
  display: inline-block;
  width: 20%;
  margin-right: 0.625%;
  text-align: center;
  line-height: 3;
  font-size: 1.4rem;
  padding: 2px 1px 0;
}

a:link {
  color: #265301;
}

a:visited {
  color: #437A16;
}

a:focus {
  border-bottom: 1px solid;
  background: #BAE498;
}

a:hover {
  border-bottom: 1px solid;
  background: #CDFEAA;
}

a:active {
  background: #265301;
  color: #CDFEAA;
}
</style>
<script type="text/javascript" src="http://code.jquery.com/jquery-1.7.1.min.js"></script>
<script>
  function filterArticles(yearFilter){
    $(".rwd-table div[class='tag_status']").each(function(){
      if (yearFilter == "ALL"){
        $(this).closest("tr").show();
      }
      else{
        if ($(this).text() == yearFilter){
            $(this).closest("tr").show();
        } else {
            $(this).closest("tr").hide();
        }      
        
      }
    });
}
  </script>

<a href="#" onclick="javascript:filterArticles('ALL');">ALL RESOURCES</a> | 
<a href="#" onclick="javascript:filterArticles('✘');">NON-COMPLIANT RESOURCES</a> | 
<a href="#" onclick="javascript:filterArticles('✔');">COMPLIANT RESOURCES</a>

<style>
@import "https://fonts.googleapis.com/css?family=Montserrat:300,400,700";
.rwd-table {
  margin: 1em 0;
  min-width: 300px;
}
.rwd-table tr {
  border-top: 1px solid #ddd;
  border-bottom: 1px solid #ddd;
}
.rwd-table th {
  display: none;
}
.rwd-table td {
  display: block;
}
.rwd-table td:first-child {
  padding-top: .5em;
}
.rwd-table td:last-child {
  padding-bottom: .5em;
}
.rwd-table td:before {
  content: attr(data-th) ": ";
  font-weight: bold;
  width: 6.5em;
  display: inline-block;
}
@media (min-width: 480px) {
  .rwd-table td:before {
    display: none;
  }
}
.rwd-table th, .rwd-table td {
  text-align: left;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    display: table-cell;
    padding: .25em .5em;
  }
  .rwd-table th:first-child, .rwd-table td:first-child {
    padding-left: 0;
  }
  .rwd-table th:last-child, .rwd-table td:last-child {
    padding-right: 0;
  }
}


h1 {
  font-weight: normal;
  letter-spacing: -1px;
  color: #34495E;
}

.rwd-table {
  background: #34495E;
  color: #fff;
  border-radius: .4em;
  overflow: hidden;
}
.rwd-table tr {
  border-color: #46637f;
}
.rwd-table th, .rwd-table td {
  margin: .5em 1em;
}
@media (min-width: 480px) {
  .rwd-table th, .rwd-table td {
    padding: 1em !important;
  }
}
.rwd-table th, .rwd-table td:before {
  color: #dd5;
}
</style>
<script>
  window.console = window.console || function(t) {};
</script>
<script>
  if (document.location.search.match(/type=embed/gi)) {
    window.parent.postMessage("resize", "*");
  }
</script>"""

def generate_html(csv_name,html_file_name, case_insensitive, pd):
  df = pd.read_csv(csv_name)
  df.to_html(html_file_name)
  with open(html_file_name) as file:
    file = file.read()
  file = file.replace("<table ", "<table class='rwd-table'")
  file = file.replace("<td>✘</td>","<td style='color:#FF0000'><div class='tag_status'>✘</div></td>")
  file = file.replace("<td>✔</td>","<td style='color:#008000'><div class='tag_status'>✔</div></td>")
  file = file.replace("<table class='rwd-table'",f"<p class='rwd-table'> Case Insensitive : {case_insensitive} </p> <table class='rwd-table'")
  with open(html_file_name, "w") as file_to_write:
    file_to_write.write(HTML + file)