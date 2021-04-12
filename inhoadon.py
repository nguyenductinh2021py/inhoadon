class BillPayView(APIView):

    def post(self, request, pk):
        table_id = pk
        if TableModel.objects.get(id=table_id, status='Có người'):
            with connection.cursor() as cursor:
                cursor.execute(f"UPDATE order_billmodel SET status= true WHERE table_id_id = {table_id}")
                cursor.execute(f"UPDATE food_table_manager_tablemodel SET status='Trống' WHERE id={table_id}")
        
            bill = PrintBill.objects.raw(f"""SELECT B.id AS "bill_id", TB.name AS "table_name"
            , B.time_created AS "time_created" , F.food_name AS "food_name"
            , BD.amount AS "amount", BD.price AS "price"
            , (BD.amount*BD.price) AS "total_price"
            FROM order_billmodel B, order_detailbillmodel BD, food_table_manager_foodmodel F, food_table_manager_tablemodel TB
            WHERE B.id = BD.bill_id_id AND BD.food_id_id = F.id AND TB.id = B.table_id_id AND B.status = false AND TB.id = {table_id}""")
        
            serializer = PrintBillSerializer(bill, many=True)
            billInfo = GetBillInfo.objects.raw(f"""SELECT B.id AS "bill_id", TB.name AS "table_name"
            , to_char(B.time_created, 'YYYY-MM-DD HH:MI:SS') as "time_created"
            , SUM(BD.amount*BD.price) AS "total_price"
            FROM order_billmodel B, order_detailbillmodel BD, food_table_manager_foodmodel F, food_table_manager_tablemodel TB
            WHERE B.id = BD.bill_id_id AND BD.food_id_id = F.id AND TB.id = B.table_id_id AND B.status = false AND TB.id = {table_id}
            GROUP BY B.id, TB.name, B.time_created, time_created""")
            bill_Info = GetBillInfoSerializer(billInfo, many=True)
            total = self.getSum(pk)  
            response = {
                "bill_id": (bill_Info.data[0])['bill_id'],
                "table_name": (bill_Info.data[0])['table_name'],
                "time_created": (bill_Info.data[0])['time_created'],
                "total_price": (bill_Info.data[0])['total_price'],
                "total": total,
                "data": serializer.data,
                "status_code": status.HTTP_200_OK
            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Bàn này không có hóa đơn", "status_code": 404}, status=status.HTTP_200_OK)
        


class GetBillInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetBillInfo
        fields = '__all__'

class PrintBillSerializer(serializers.ModelSerializer):
    class Meta:
        model=PrintBill
        fields=['food_name', 'price', 'amount', 'total_price']

class GetBillInfo(models.Model):
    bill_id = models.IntegerField(primary_key=True)
    table_name = models.CharField(max_length=255)
    time_created = models.DateTimeField()
    total_price = models.IntegerField()

class PrintBill(models.Model):
    bill_id = models.IntegerField(primary_key=True)
    table_name = models.CharField(max_length=255)
    time_created = models.DateTimeField()
    food_name = models.CharField(max_length=255)
    price = models.IntegerField()
    amount = models.IntegerField()
    total_price = models.IntegerField()