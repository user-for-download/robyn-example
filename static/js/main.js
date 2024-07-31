async function createBarChart(selector, dataChar) {
    const data = dataChar.sort((a, b) => b.count - a.count).slice(0, 8);
    const width = 450, height = 250;
    const marginTop = 20, marginRight = 0, marginBottom = 40, marginLeft = 40;
    const x = d3.scaleBand().domain(d3.sort(data, d => -d.count).map(d => d.id))
        .range([marginLeft, width - marginRight]).padding(0.1);
    const xAxis = d3.axisBottom(x).tickSize(0);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).nice()
        .range([height - marginBottom, marginTop]);

    const svg = d3.select(selector).append("svg")
        .attr("viewBox", `0 0 ${width} ${height}`)
        .attr("width", width)
        .attr("height", height)
        .attr("style", "max-width: 100%; height: auto;");

    svg.append("g").attr("class", "bars").attr("fill", "steelblue")
        .selectAll("rect").data(data).join("rect")
        .attr("x", d => x(d.id)).attr("y", d => y(d.count))
        .attr("height", d => y(0) - y(d.count)).attr("width", x.bandwidth());

    svg.append("g").attr("class", "x-axis")
        .attr("transform", `translate(0,${height - marginBottom})`)
        .call(xAxis).selectAll(".tick text").remove();

    svg.selectAll(".x-axis .tick").append("svg:image")
        .attr("xlink:href", d => data.find(item => item.id === d).image)
        .attr("width", 50).attr("height", 30)
        .attr("x", -25).attr("y", 10);

    svg.append("g").attr("class", "y-axis")
        .attr("transform", `translate(${marginLeft},0)`)
        .call(d3.axisLeft(y)).call(g => g.select(".domain").remove());

    function zoom(svg) {
        const extent = [[marginLeft, marginTop], [width - marginRight, height - marginTop]];
        svg.call(d3.zoom().scaleExtent([1, 8]).translateExtent(extent)
            .extent(extent).on("zoom", zoomed));

        function zoomed(event) {
            x.range([marginLeft, width - marginRight].map(d => event.transform.applyX(d)));
            svg.selectAll(".bars rect").attr("x", d => x(d.id)).attr("width", x.bandwidth());
            svg.selectAll(".x-axis").call(xAxis);
            svg.selectAll(".x-axis image").attr("x", d => x(d)).attr("width", x.bandwidth());
        }
    }

    return svg.node();
}

async function showProgressBar(idSelector) {
    const divPr = document.getElementById(idSelector);
    divPr.classList.add('progress')
    divPr.innerHTML = '<div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100" style="width: 100%"></div>'
    return divPr;
}

async function removeProgressBar(progressBar) {
    if (progressBar) {
        progressBar.remove();
    }
}

async function fetchDataAndCreateCharts(query, idProgress) {
    const progressBar = await showProgressBar(idProgress);

    function searchParamsToObj(url) {
        const paramsMap = Array
            .from(url.searchParams)
            .reduce((params, [key, val]) => params.set(key, val), new Map());
        return Object.fromEntries(paramsMap);
    }

    try {
        const url = new URL('/match/picks?' + query, window.location.origin);
        // let leagueId, teamId, startDateTime, durationSeconds;
        // if (leagueId) url.searchParams.append('league_id', leagueId);
        // if (teamId) url.searchParams.append('team_id', teamId);
        // if (startDateTime) url.searchParams.append('start_date_time', startDateTime);
        // if (durationSeconds) url.searchParams.append('duration_seconds', durationSeconds);

        const response = await fetch(url);
        const data = await response.json();
        if (data.error) {
            console.error('Error fetching heroes data:', data.error);
            return null;
        } else {
            return data;
        }
    } catch (error) {
        console.error('Error fetching heroes data:', error);
        return null;
    } finally {
        await removeProgressBar(progressBar);
    }
}