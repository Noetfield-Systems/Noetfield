"""Playwright waits for Evidence Lab films — cockpit must show live work, not placeholders."""


def wait_cockpit_connected(page, timeout: int = 120_000) -> None:
    page.wait_for_function(
        """() => {
          const el = document.querySelector('#project-status');
          return el && !/connecting/i.test((el.textContent || '').trim());
        }""",
        timeout=timeout,
    )


def wait_cockpit_working(page, timeout: int = 180_000) -> None:
    wait_cockpit_connected(page, timeout)
    page.wait_for_function(
        """() => {
          const chat = document.querySelectorAll('#agent-messages .agent-msg').length;
          const tasks = (document.querySelector('#tasks-list') || {}).textContent || '';
          const roster = (document.querySelector('#team-roster') || {}).textContent || '';
          const ticker = (document.querySelector('#live-activity-list') || {}).textContent || '';
          const workingTasks = !/no work started yet/i.test(tasks);
          const rosterLive = !/standing by/i.test(roster);
          const tickerLive = /build|motor|quality|delivery|hiring|working|publish|team|front person/i.test(ticker);
          return chat > 0 && (workingTasks || rosterLive || tickerLive);
        }""",
        timeout=timeout,
    )


def wait_cockpit_delivered(page, timeout: int = 180_000) -> None:
    wait_cockpit_connected(page, timeout)
    page.wait_for_function(
        """() => {
          const docLink = document.querySelector('#documents-list a[href]');
          const siteBtn = document.querySelector('#site-open:not([hidden]), #live-open:not([hidden])');
          const previewFrame = document.querySelector('#site-preview:not([hidden]) iframe[src]');
          const agentStatus = (document.querySelector('#agent-status') || {}).textContent || '';
          const agentReady = /ready|download|preview/i.test(agentStatus);
          const siteMeta = (document.querySelector('#deployment-meta') || {}).textContent || '';
          const siteLive = /live|preview ready/i.test(siteMeta);
          return !!(docLink || siteBtn || previewFrame) && (agentReady || siteLive);
        }""",
        timeout=timeout,
    )
