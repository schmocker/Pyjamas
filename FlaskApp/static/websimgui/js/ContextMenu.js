class ContextMenu {
    constructor(parent) {
        this.parent = parent;
        this.parent.append('div')
            .attr('class', 'context-menu');


        d3.select('body').on('click.context-menu', function() {
            d3.select('.context-menu').style('display', 'none');
        });
    }

    onContextMenu (menu) {

        // this gets executed when a contextmenu event occurs
        return function(data, index) {
            console.log("context menu triggerd");

            let elm = this;

            d3.selectAll('.context-menu').html('');
            let list = d3.selectAll('.context-menu').append('ul');
            list.selectAll('li').data(menu).enter()
                .append('li')
                .html(function(d) {return d.title;})
                .on('click', function(d, i) {
                    d.action(elm, data, index);
                    d3.select('.context-menu').style('display', 'none');
                });

            // display context menu
            d3.select('.context-menu')
                .style('left', (d3.event.pageX - 2) + 'px')
                .style('top', (d3.event.pageY - 2) + 'px')
                .style('display', 'block');

            d3.event.preventDefault();
        };
    }
}

