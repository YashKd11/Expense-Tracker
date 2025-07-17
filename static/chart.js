const ctx1 = document.getElementById('expenseChart1').getContext('2d');
const ctx2 = document.getElementById('expenseChart2').getContext('2d');
const backgroundColor = [
  '#2C3E50', '#3B3B3B', '#4B627A',
  '#2F4F4F', '#7E6651', '#708090',
  '#6A5ACD', '#003B46'
];


new Chart(ctx2, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Expense Distribution',
            data: values,
            backgroundColor: backgroundColor,
            borderColor: '#fff',
            borderWidth: 1
        }]
    },
    options: {
        resposive: true,
        plugins:{
            position: 'top',
            legend:{
                color: '#fff'
            }
        }
    }
})


new Chart(ctx1, {
  type: 'pie',
  data: {
    labels: labels,
    datasets: [{
      label: 'Expense Distribution',
      data: values,
      backgroundColor: backgroundColor,
      borderColor: '#fff',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
            color:'#fff'
        }
      }
    }
  }
});
