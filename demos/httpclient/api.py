from wheezy.core.httpclient import HTTPClient

client = HTTPClient("http://buildbot.buildbot.net/json/")
assert 200 == client.get("project")
project = client.json
assert "Buildbot" == project.title
