from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from pathlib import Path
import json
import sqlite3
import tempfile


def checkTelemetryEvents(aDriver, full=False):
    get_events_js = """
        const { TelemetryController } = ChromeUtils.importESModule(
          "resource://gre/modules/TelemetryController.sys.mjs"
        );
        const Telemetry = Services.telemetry;
        let ping = TelemetryController.getCurrentPingData(true);
        let eventSnapshot = Telemetry.snapshotEvents(
          Telemetry.DATASET_PRERELEASE_CHANNELS, false);
        Object.keys(eventSnapshot).forEach(process => {
          if (process in ping.payload.processes) {
            ping.payload.processes[process].events = eventSnapshot[process].filter(
              e => !e[1].startsWith("telemetry.test"));
          }
        });
        return JSON.stringify(ping, null, 2);
    """

    aDriver.get("about:telemetry#events-tab")
    snapshot = aDriver.execute_script(get_events_js)
    snapshot_json = json.loads(snapshot)
    if full:
        print(snapshot_json)
        return

    simplified = []
    procs = snapshot_json["payload"]["processes"]
    for k, v in procs.items():
        if 'events' in v.keys():
            simplified.append({k: v['events']})
    column_names = ['timestamp', 'category', 'method', 'object', 'value', 'extra']
    print(simplified)


def makeDriver(specified_profile):
    options = webdriver.FirefoxOptions()
    options.binary_location = "/opt/bin/firefox/firefox-bin"
    options.add_argument("--headless")
    options.add_argument("--profile")
    options.add_argument(specified_profile)

    options.set_preference("dom.storage.default_quota", 0)
    options.set_preference("dom.storage.default_site_quota", 0)

    result = webdriver.Firefox(options=options)
    # options.set_preference("toolkit.telemetry.testing.overrideProductsCheck", True)
    # options.set_preference("toolkit.telemetry.server", "localhost:9387")

    return result


def perform_broken_site_load():
    with tempfile.TemporaryDirectory() as tmpdirname:
        firefox_profile = tmpdirname
        driver = makeDriver(firefox_profile)
        
        # Find the profile directory
        driver.get("about:support")
        driver.implicitly_wait(10)
        profile_dir = driver.find_element(By.ID, "profile-dir-box").text
        print("PROFILE DIR:", profile_dir)
        profile_path = Path(profile_dir)
    
        
        # Are the quota prefs as expected?
        with open(profile_path / "user.js") as prefs_file:
            for line in prefs_file:
                for pref in quota_prefs:
                    if line.includes(
                            "dom.storage.default_quota"
                            ) or line.includes(
                            "dom.storage.default_site_quota"):
                        print(line)

        # Trigger the issue
        driver.get("http://brokensite.com/emit_telemetry.html")
        driver.find_element(By.ID, "startButton").click()
        result = driver.find_element(By.ID, "outcomeDiv")
        
        # Check if we got anything
        wait = WebDriverWait(driver, timeout=60, poll_frequency=.2).until(
            lambda d : len(result.text) > 0)
        print("RESULT:", result.text)
        
        msg = driver.find_element(By.ID, "messageDiv")
        if msg.text:
            print("MESSAGE:", msg.text)
        
        print("checking telemetry")
        checkTelemetryEvents(driver, full=False)

        driver.quit()


def application(env, start_response):
    try:
        perform_broken_site_load()
        start_response('200 OK', [('Content-Type','text/html')])
        return [b"SUCCESS"]
    except Exception as err:
        start_response('500 INTERNAL SERVER ERROR', [('Content-Type','text/html')])
        return [repr(err).encode('utf-8')]

