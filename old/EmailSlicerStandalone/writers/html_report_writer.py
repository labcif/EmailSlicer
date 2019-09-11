import os
import jinja2
import json
import sys

class Report:

    def __init__(self, output_directory, report_title, total_email_address, totals_data, path, senders_data, heatmap_data, users_communication_data, user_messages_date):
        self.total_email_messages, self.total_events, self.total_contacts = self.totals(totals_data)
        self.total_email_address = total_email_address
        self.folders_struct = self.folders(path)
        self.senders_frequency = self.senders(senders_data)
        self.received_time_heatmap = self.heatmap(heatmap_data)
        self.title = report_title
        self.output_directory = output_directory
        self.users_communication_table = self.parse_json_to_table(users_communication_data, 'row_id', 'sender', 'receiver', 'count').replace('\n', '').encode('utf8')
        self.users_messages_table = self.parse_json_to_table(user_messages_date, 'row_id', 'subject', 'location', 'date').replace('\n', '').encode('utf8')
        self.run()


    def run(self):
        path = sys.argv[0].replace("EmailSlicer.py", '')
        open_template1 = open("{}utils/report_template1.html".format(path), 'r').read()
        open_template2 = open("{}utils/report_template2.html".format(path), 'r').read()
        html_template1 = jinja2.Template(open_template1)
        html_template2 = jinja2.Template(open_template2)
        
        folder_struncture = """
            <div 
                id="folders" 
                style="height: 50%; width: 80%; display: block;margin-left: auto;margin-right: auto;">
            </div>
            <script type="text/javascript">
                var folders = echarts.init(document.getElementById("folders"));
                var app1 = {{}};
                folders_option = null;
                folders.showLoading();
                folders.hideLoading();
                folder_struncture = {0};
                echarts.util.each(folder_struncture.children, function (datum, index) 
                {{
                    index % 2 === 0 && (datum.collapsed = true);
                }});
                folders.setOption(folders_option = 
                {{
                    tooltip: 
                    {{
                        trigger: 'item',
                        triggerOn: 'mousemove'
                    }},
                    series: 
                    [
                        {{
                            type: 'tree',
                            data: [folder_struncture],
                            top: '1%',
                            left: '7%',
                            bottom: '1%',
                            right: '20%',
                            symbolSize: 7,
                            label: 
                            {{
                                normal: 
                                {{
                                    position: 'left',
                                    verticalAlign: 'middle',
                                    align: 'right',
                                    fontSize: 9
                                }}
                            }},
                            leaves: 
                            {{
                                label: 
                                {{
                                    normal: 
                                    {{
                                        position: 'right',
                                        verticalAlign: 'middle',
                                        align: 'left'
                                    }}
                                }}
                            }},
                            expandAndCollapse: true,
                            animationDuration: 550,
                            animationDurationUpdate: 750
                        }}
                    ]
                }});
                if (folders_option && typeof folders_option === "object") 
                {{
                    folders.setOption(folders_option, true);
                }}
            </script>
        """.format(self.folders_struct)

        bargraph = """
            <div id="bargrapgh" style="height: 50%; width: 80%; display: block; margin-left: auto; margin-right: auto;"></div>
            <script type="text/javascript">
                var bargraph = echarts.init(document.getElementById("bargrapgh"));
                var app2 = {{}};
                bargraph_option = null;
                senders = {0};
                bargraph_option = 
                {{
                    tooltip : 
                    {{
                        trigger: 'axis',
                        axisPointer: 
                        {{
                            type: 'shadow',
                            label: 
                            {{
                                show: true
                            }}
                        }}
                    }},
                    calculable : true,
                    legend: 
                    {{
                        data:['Growth', 'Budget 2011'],
                        itemGap: 5
                    }},
                    grid: 
                    {{
                        top: '10%',
                        left: '3%',
                        right: '10%',
                        containLabel: true
                    }},
                    xAxis: 
                    [
                        {{
                            type : 'category',
                            data : senders.emails
                        }}
                    ],
                    yAxis: 
                    [
                        {{
                            type : 'value',
                            name : 'Messages Sent',
                            axisLabel: 
                            {{
                                formatter: function (a) 
                                {{
                                    a = +a;
                                    return isFinite(a)
                                        ? echarts.format.addCommas(+a)
                                        : '';
                                }}
                            }}
                        }}
                    ],
                    dataZoom: 
                    [
                        {{
                            show: true,
                            start: 94,
                            end: 100
                        }},
                        {{
                            type: 'inside',
                            start: 94,
                            end: 100
                        }},
                        {{
                            show: true,
                            yAxisIndex: 0,
                            filterMode: 'empty',
                            width: 30,
                            height: '80%',
                            showDataShadow: false,
                            left: '93%'
                        }}
                    ],
                    series : 
                    [
                        {{
                            type: 'bar',
                            data: senders.count
                        }}
                        
                    ]
                }};
                bargraph.setOption(bargraph_option);
                if (bargraph_option && typeof bargraph_option === "object")
                {{
                    bargraph.setOption(bargraph_option, true);
                }}
            </script>
        """.format(self.senders_frequency)

        heatmap = """
            <div id="heatmap" style="height: 30%; width: 92%; display: block; margin-left: auto;margin-right: auto;"></div>
            <script type="text/javascript">
                var heatmap = echarts.init(document.getElementById("heatmap"));
                var app3 = {{}};
                heatmap_option = null;
                app3.title = 'Heatmap'; 
                var hours = ['12a', '1a', '2a', '3a', '4a', '5a', '6a',
                        '7a', '8a', '9a','10a','11a',
                        '12p', '1p', '2p', '3p', '4p', '5p',
                        '6p', '7p', '8p', '9p', '10p', '11p'];
                var days = ['Saturday', 'Friday', 'Thursday',
                        'Wednesday', 'Tuesday', 'Monday', 'Sunday'];
                var data = {0};
                function getMax(a)
                {{
                    return Math.max(...a.map(e => Array.isArray(e) ? getMax(e) : e));
                }}
                max = getMax(data)
                data = data.map(function (item) {{
                    return [item[1], item[0], item[2] || '-'];
                }});
                
                heatmap_option = 
                {{
                    tooltip: 
                    {{
                        position: 'top'
                    }},
                    animation: false,
                    grid: 
                    {{
                        height: '50%',
                        y: '10%'
                    }},
                    xAxis: 
                    {{
                        type: 'category',
                        data: hours,
                        splitArea: 
                        {{
                            show: true
                        }}
                    }},
                    yAxis: 
                    {{
                        type: 'category',
                        data: days,
                        splitArea: 
                        {{
                            show: true
                        }}
                    }},
                    visualMap: 
                    {{
                        min: 0,
                        max: max,
                        calculable: true,
                        orient: 'horizontal',
                        left: 'center',
                        bottom: '15%'
                    }},
                    series: 
                    [
                        {{
                            name: 'Emails Received',
                            type: 'heatmap',
                            data: data,
                            label: 
                            {{
                                normal: 
                                {{
                                    show: true
                                }}
                            }},
                            itemStyle:
                            {{
                                emphasis: 
                                {{
                                    shadowBlur: 10,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }}
                            }}
                        }}
                    ]
                }};
                heatmap.setOption(heatmap_option, true);
            </script>
        """.format(self.received_time_heatmap)

        #context = {"report_title": report_title, "pst_name": pst_name}
        context1 = {
            'title': self.title,
            'total_email_messages': self.total_email_messages,
            'total_email_address': self.total_email_address,
            'total_contacts': self.total_contacts,
            'total_events': self.total_events,
            'bargraph': bargraph,
            'heatmap': heatmap, 
            'folder_struncture': folder_struncture,
        }

        context2 = {
            'title': self.title,
            'users_communication': self.users_communication_table,
            'users_messages': self.users_messages_table

        } 
        
        new_html1 = html_template1.render(context1)
        new_html2 = html_template2.render(context2)

        html_report_file1 = open(self.output_directory + '/' + self.title + '1.html', 'w+')
        html_report_file2 = open(self.output_directory + '/' + self.title + '2.html', 'w+')
        
        html_report_file1.write(new_html1)
        html_report_file2.write(new_html2)
        
        html_report_file1.close()
        html_report_file2.close()


    def totals(self, data):
        
        count_ics = 0
        count_vcf = 0
        count_eml = 0
        
        for ics, vcf, eml, _ in data:
            count_ics += ics
            count_vcf += vcf
            count_eml += eml

        return count_eml, count_ics, count_vcf


    def folders(self, path):

        return_data = {'name': os.path.basename(path)}
        
        if os.path.isdir(path):
            return_data['type'] = "directory"
            return_data['children'] = [self.folders(os.path.join(path,x)) for x in os.listdir(path)]
        else:
            return_data['type'] = "file"
        
        return return_data
    

    def senders(self, sender_frequency):

        emails = []
        count = []
        
        for sender_count in sender_frequency: 
            emails.append(sender_count['email'])
            count.append(sender_count['count'])
        
        sorted_emails = [x for _,x in sorted(zip(count, emails))]
        sorted_count = sorted(count)
        
        return_data = {
            'emails': sorted_emails,
            'count': sorted_count
        }
        
        return json.dumps(return_data)

    
    def heatmap(self, date_list):
    
        return_data = []

        for date, hours_list in enumerate(date_list):
            for hour, count in hours_list.items():
                return_data.append([date, hour - 1, count])
        
        return return_data

    def parse_json_to_table(self, json, first, secound, third, fourth):
        string = ''
        for field in json:
            if field:
                string += '''
                    <tr>
                        <th scope = "row"> {} </th >
                        <td> {} </td>
                        <td> {} </td>
                        <td> {} </td>
                    </tr>\n
                '''.format(field[first], field[secound], field[third], field[fourth])
        return string